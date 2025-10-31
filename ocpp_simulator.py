#!/usr/bin/env python3
"""
OCPP 1.6 Charging Station Simulator
Supports RemoteStartTransaction and sends real-time charging data
"""

import asyncio
import json
import uuid
import websockets
from datetime import datetime
from enum import Enum
from typing import Optional
import sys


class ChargePointStatus(Enum):
    AVAILABLE = "Available"
    PREPARING = "Preparing"
    CHARGING = "Charging"
    SUSPENDED_EVSE = "SuspendedEVSE"
    SUSPENDED_EV = "SuspendedEV"
    FINISHING = "Finishing"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"


class ChargePointErrorCode(Enum):
    NO_ERROR = "NoError"
    CONNECTOR_LOCK_FAILURE = "ConnectorLockFailure"
    EV_COMMUNICATION_ERROR = "EVCommunicationError"
    GROUND_FAILURE = "GroundFailure"
    HIGH_TEMPERATURE = "HighTemperature"
    INTERNAL_ERROR = "InternalError"
    LOCAL_LIST_CONFLICT = "LocalListConflict"
    OTHER_ERROR = "OtherError"
    OVER_CURRENT_FAILURE = "OverCurrentFailure"
    POWER_METER_FAILURE = "PowerMeterFailure"
    POWER_SWITCH_FAILURE = "PowerSwitchFailure"
    READER_FAILURE = "ReaderFailure"
    RESET_FAILURE = "ResetFailure"
    UNDER_VOLTAGE = "UnderVoltage"
    OVER_VOLTAGE = "OverVoltage"
    WEAK_SIGNAL = "WeakSignal"


class OCPP16ChargePoint:
    def __init__(self, charge_point_id: str, central_system_url: str):
        self.charge_point_id = charge_point_id
        self.central_system_url = central_system_url
        self.websocket = None
        self.status = ChargePointStatus.AVAILABLE
        self.error_code = ChargePointErrorCode.NO_ERROR
        self.connector_id = 1
        self.transaction_id: Optional[int] = None
        self.id_tag: Optional[str] = None
        self.meter_value = 0
        self.charging_current = 0.0
        self.charging_voltage = 230.0
        self.charging_power = 0.0
        self.is_charging = False
        self.battery_soc = 20.0  # Start with 20% battery
        self.message_queue = asyncio.Queue()
        
    async def connect(self):
        """Connect to Central System"""
        url = f"{self.central_system_url}/{self.charge_point_id}"
        print(f"🔌 Connecting to Central System: {url}")
        
        try:
            self.websocket = await websockets.connect(
                url,
                subprotocols=["ocpp1.6"]
            )
            print(f"✅ Connected to Central System")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def send_message(self, message: list):
        """Send OCPP message"""
        message_json = json.dumps(message)
        print(f"📤 Sending: {message_json}")
        await self.websocket.send(message_json)
    
    async def send_call(self, action: str, payload: dict) -> str:
        """Send OCPP Call message"""
        unique_id = str(uuid.uuid4())
        message = [2, unique_id, action, payload]
        await self.send_message(message)
        return unique_id
    
    async def send_call_result(self, unique_id: str, payload: dict):
        """Send OCPP CallResult message"""
        message = [3, unique_id, payload]
        await self.send_message(message)
    
    async def send_call_error(self, unique_id: str, error_code: str, error_description: str):
        """Send OCPP CallError message"""
        message = [4, unique_id, error_code, error_description, {}]
        await self.send_message(message)
    
    async def send_boot_notification(self):
        """Send BootNotification"""
        payload = {
            "chargePointVendor": "SimulatorVendor",
            "chargePointModel": "Simulator-1.0",
            "chargePointSerialNumber": f"SIM-{self.charge_point_id}",
            "firmwareVersion": "1.0.0",
            "iccid": "",
            "imsi": "",
            "meterType": "SmartMeter",
            "meterSerialNumber": "METER-001"
        }
        await self.send_call("BootNotification", payload)
    
    async def send_status_notification(self, status: ChargePointStatus, error_code: ChargePointErrorCode = ChargePointErrorCode.NO_ERROR):
        """Send StatusNotification"""
        self.status = status
        self.error_code = error_code
        
        payload = {
            "connectorId": self.connector_id,
            "errorCode": error_code.value,
            "status": status.value,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        await self.send_call("StatusNotification", payload)
        print(f"📊 Status changed: {status.value}")
    
    async def send_start_transaction(self, id_tag: str):
        """Send StartTransaction"""
        payload = {
            "connectorId": self.connector_id,
            "idTag": id_tag,
            "meterStart": self.meter_value,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        await self.send_call("StartTransaction", payload)
    
    async def send_stop_transaction(self, reason: str = "Local"):
        """Send StopTransaction"""
        if self.transaction_id is None:
            print("⚠️  No active transaction to stop")
            return
        
        payload = {
            "transactionId": self.transaction_id,
            "meterStop": self.meter_value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason
        }
        
        if self.id_tag:
            payload["idTag"] = self.id_tag
        
        await self.send_call("StopTransaction", payload)
    
    async def send_meter_values(self):
        """Send MeterValues with current charging data"""
        if self.transaction_id is None:
            return
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        payload = {
            "connectorId": self.connector_id,
            "transactionId": self.transaction_id,
            "meterValue": [
                {
                    "timestamp": timestamp,
                    "sampledValue": [
                        {
                            "value": str(self.meter_value),
                            "context": "Sample.Periodic",
                            "format": "Raw",
                            "measurand": "Energy.Active.Import.Register",
                            "unit": "Wh"
                        },
                        {
                            "value": f"{self.charging_current:.2f}",
                            "context": "Sample.Periodic",
                            "format": "Raw",
                            "measurand": "Current.Import",
                            "phase": "L1",
                            "unit": "A"
                        },
                        {
                            "value": f"{self.charging_voltage:.2f}",
                            "context": "Sample.Periodic",
                            "format": "Raw",
                            "measurand": "Voltage",
                            "phase": "L1",
                            "unit": "V"
                        },
                        {
                            "value": f"{self.charging_power:.2f}",
                            "context": "Sample.Periodic",
                            "format": "Raw",
                            "measurand": "Power.Active.Import",
                            "unit": "W"
                        },
                        {
                            "value": f"{self.battery_soc:.1f}",
                            "context": "Sample.Periodic",
                            "format": "Raw",
                            "measurand": "SoC",
                            "unit": "Percent"
                        }
                    ]
                }
            ]
        }
        
        await self.send_call("MeterValues", payload)
        print(f"⚡ Meter: {self.meter_value}Wh | Current: {self.charging_current:.2f}A | Power: {self.charging_power:.2f}W | Battery: {self.battery_soc:.1f}%")
    
    async def send_heartbeat(self):
        """Send Heartbeat"""
        await self.send_call("Heartbeat", {})
    
    async def handle_remote_start_transaction(self, payload: dict):
        """Handle RemoteStartTransaction request"""
        connector_id = payload.get("connectorId", 1)
        id_tag = payload["idTag"]
        
        print(f"🚀 RemoteStartTransaction received for connector {connector_id}, idTag: {id_tag}")
        
        # OCPP 1.6: Only accept RemoteStartTransaction when Available
        if self.status != ChargePointStatus.AVAILABLE:
            print(f"⚠️  Rejected - connector must be Available (current: {self.status.value})")
            return {"status": "Rejected"}
        
        # Check if already in transaction
        if self.transaction_id is not None:
            print(f"⚠️  Rejected - transaction {self.transaction_id} already active")
            return {"status": "Rejected"}
        
        self.id_tag = id_tag
        
        # Start transaction sequence automatically
        asyncio.create_task(self.auto_start_transaction(id_tag))
        
        return {"status": "Accepted"}
    
    async def auto_start_transaction(self, id_tag: str):
        """Automatically handle transaction start sequence"""
        try:
            # 1. Change to Preparing
            await self.send_status_notification(ChargePointStatus.PREPARING)
            await asyncio.sleep(2)
            
            # 2. Send StartTransaction
            await self.send_start_transaction(id_tag)
            await asyncio.sleep(1)
            
            # Wait for transaction ID from response (will be set by message handler)
            for _ in range(10):
                if self.transaction_id is not None:
                    break
                await asyncio.sleep(0.5)
            
            if self.transaction_id is None:
                print("⚠️  Transaction ID not received")
                await self.send_status_notification(ChargePointStatus.AVAILABLE)
                return
            
            # 3. Change to Charging
            await self.send_status_notification(ChargePointStatus.CHARGING)
            self.is_charging = True
            
            # Start charging simulation
            asyncio.create_task(self.simulate_charging())
            
            print(f"✅ Transaction {self.transaction_id} started successfully")
            
        except Exception as e:
            print(f"❌ Error in auto start: {e}")
            await self.send_status_notification(ChargePointStatus.AVAILABLE)
    
    async def simulate_charging(self):
        """Simulate charging process with meter values"""
        import random
        
        # Charging parameters
        self.charging_current = 16.0  # 16A
        self.charging_voltage = 230.0  # 230V
        self.charging_power = self.charging_current * self.charging_voltage  # ~3680W
        
        # Battery simulation (assuming ~50kWh battery capacity)
        battery_capacity_wh = 50000  # 50 kWh
        
        print(f"🔋 Charging started: {self.charging_current}A @ {self.charging_voltage}V = {self.charging_power}W | Battery: {self.battery_soc:.1f}%")
        
        while self.is_charging and self.transaction_id is not None:
            # Stop if battery is full
            if self.battery_soc >= 100.0:
                print("🔋 Battery full (100%) - stopping charge")
                self.battery_soc = 100.0
                await asyncio.sleep(2)
                await self.auto_stop_transaction("EVDisconnected")
                break
            
            # Increment energy faster - simulate 60 seconds worth of charging every 5 seconds
            energy_increment = (self.charging_power / 3600) * 60  # 60 seconds worth
            self.meter_value += int(energy_increment)
            
            # Update battery SoC based on energy added
            # Increment = (energy_added / battery_capacity) * 100
            soc_increment = (energy_increment / battery_capacity_wh) * 100
            self.battery_soc += soc_increment
            
            # Limit to 100%
            if self.battery_soc > 100.0:
                self.battery_soc = 100.0
            
            # Add some variation to current (less current as battery gets fuller)
            charging_rate = 1.0 if self.battery_soc < 80 else (100 - self.battery_soc) / 20
            self.charging_current = (16.0 * charging_rate) + random.uniform(-0.5, 0.5)
            self.charging_power = self.charging_current * self.charging_voltage
            
            # Send meter values every 5 seconds
            await self.send_meter_values()
            await asyncio.sleep(5)
    
    async def handle_remote_stop_transaction(self, payload: dict):
        """Handle RemoteStopTransaction request"""
        transaction_id = payload["transactionId"]
        
        print(f"🛑 RemoteStopTransaction received for transaction {transaction_id}")
        
        if self.transaction_id != transaction_id:
            return {"status": "Rejected"}
        
        asyncio.create_task(self.auto_stop_transaction("Remote"))
        
        return {"status": "Accepted"}
    
    async def auto_stop_transaction(self, reason: str = "Local"):
        """Automatically handle transaction stop sequence"""
        try:
            self.is_charging = False
            self.charging_current = 0.0
            self.charging_power = 0.0
            
            # 1. Change to Finishing
            await self.send_status_notification(ChargePointStatus.FINISHING)
            await asyncio.sleep(2)
            
            # 2. Send StopTransaction
            await self.send_stop_transaction(reason)
            await asyncio.sleep(1)
            
            # 3. Change back to Available
            await self.send_status_notification(ChargePointStatus.AVAILABLE)
            
            self.transaction_id = None
            self.id_tag = None
            self.battery_soc = 20.0  # Reset to 20% for next charge
            
            print(f"✅ Transaction stopped successfully")
            
        except Exception as e:
            print(f"❌ Error in auto stop: {e}")
    
    async def handle_message(self, message_text: str):
        """Handle incoming OCPP message"""
        try:
            message = json.loads(message_text)
            print(f"📥 Received: {message_text}")
            
            message_type = message[0]
            
            if message_type == 2:  # CALL
                unique_id = message[1]
                action = message[2]
                payload = message[3]
                
                if action == "RemoteStartTransaction":
                    result = await self.handle_remote_start_transaction(payload)
                    await self.send_call_result(unique_id, result)
                
                elif action == "RemoteStopTransaction":
                    result = await self.handle_remote_stop_transaction(payload)
                    await self.send_call_result(unique_id, result)
                
                elif action == "Reset":
                    result = {"status": "Accepted"}
                    await self.send_call_result(unique_id, result)
                    print("🔄 Reset accepted")
                
                elif action == "ChangeConfiguration":
                    result = {"status": "Accepted"}
                    await self.send_call_result(unique_id, result)
                
                else:
                    await self.send_call_error(unique_id, "NotImplemented", f"Action {action} not implemented")
            
            elif message_type == 3:  # CALLRESULT
                unique_id = message[1]
                payload = message[2]
                
                # Handle StartTransaction response
                if "idTagInfo" in payload and "transactionId" in payload:
                    self.transaction_id = payload["transactionId"]
                    print(f"✅ Transaction ID: {self.transaction_id}")
            
            elif message_type == 4:  # CALLERROR
                print(f"❌ Error received: {message}")
        
        except Exception as e:
            print(f"❌ Error handling message: {e}")
    
    async def message_receiver(self):
        """Receive messages from Central System"""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("⚠️  Connection closed")
        except Exception as e:
            print(f"❌ Receiver error: {e}")
    
    async def heartbeat_loop(self):
        """Send periodic heartbeats"""
        while True:
            await asyncio.sleep(60)
            try:
                await self.send_heartbeat()
            except Exception as e:
                print(f"❌ Heartbeat error: {e}")
                break
    
    async def cli_control_panel(self):
        """CLI control panel for manual status changes"""
        print("\n" + "="*60)
        print("🎛️  CLI CONTROL PANEL")
        print("="*60)
        print("Commands:")
        print("  status <status>  - Change status (available, charging, faulted, etc.)")
        print("  error <code>     - Set error code (NoError, GroundFailure, etc.)")
        print("  start <idTag>    - Start transaction manually")
        print("  stop             - Stop current transaction")
        print("  current <amps>   - Set charging current (A)")
        print("  info             - Show current state")
        print("  help             - Show this help")
        print("  quit             - Exit simulator")
        print("="*60 + "\n")
        
        try:
            from aioconsole import ainput
            
            while True:
                try:
                    cmd = await ainput(">>> ")
                    cmd = cmd.strip()
                    
                    if not cmd:
                        continue
                    
                    parts = cmd.split(maxsplit=1)
                    command = parts[0].lower()
                    arg = parts[1] if len(parts) > 1 else None
                    
                    if command == "quit" or command == "exit":
                        print("👋 Exiting...")
                        await self.auto_stop_transaction("Local")
                        break
                    
                    elif command == "status":
                        if not arg:
                            print("Usage: status <status_name>")
                            continue
                        try:
                            status = ChargePointStatus[arg.upper().replace(" ", "_")]
                            await self.send_status_notification(status)
                        except KeyError:
                            print(f"Invalid status. Options: {', '.join([s.name for s in ChargePointStatus])}")
                    
                    elif command == "error":
                        if not arg:
                            print("Usage: error <error_code>")
                            continue
                        try:
                            error = ChargePointErrorCode[arg.upper().replace(" ", "_")]
                            await self.send_status_notification(self.status, error)
                        except KeyError:
                            print(f"Invalid error code. Options: {', '.join([e.name for e in ChargePointErrorCode])}")
                    
                    elif command == "start":
                        if not arg:
                            print("Usage: start <idTag>")
                            continue
                        await self.auto_start_transaction(arg)
                    
                    elif command == "stop":
                        await self.auto_stop_transaction("Local")
                    
                    elif command == "current":
                        if not arg:
                            print("Usage: current <amps>")
                            continue
                        try:
                            self.charging_current = float(arg)
                            self.charging_power = self.charging_current * self.charging_voltage
                            print(f"⚡ Current set to {self.charging_current}A, Power: {self.charging_power}W")
                        except ValueError:
                            print("Invalid current value")
                    
                    elif command == "info":
                        print(f"\n📊 Current State:")
                        print(f"  Status: {self.status.value}")
                        print(f"  Error: {self.error_code.value}")
                        print(f"  Transaction ID: {self.transaction_id}")
                        print(f"  ID Tag: {self.id_tag}")
                        print(f"  Meter: {self.meter_value} Wh")
                        print(f"  Current: {self.charging_current:.2f} A")
                        print(f"  Voltage: {self.charging_voltage:.2f} V")
                        print(f"  Power: {self.charging_power:.2f} W")
                        print(f"  Battery SoC: {self.battery_soc:.1f} %")
                        print(f"  Charging: {self.is_charging}\n")
                    
                    elif command == "help":
                        await self.cli_control_panel()
                        return
                    
                    else:
                        print(f"Unknown command: {command}. Type 'help' for commands.")
                
                except EOFError:
                    break
                except Exception as e:
                    print(f"❌ Command error: {e}")
        
        except ImportError:
            print("⚠️  aioconsole not available, CLI disabled")
    
    async def run(self):
        """Run the charge point simulator"""
        if not await self.connect():
            return
        
        # Send BootNotification
        await self.send_boot_notification()
        await asyncio.sleep(1)
        
        # Send initial status
        await self.send_status_notification(ChargePointStatus.AVAILABLE)
        
        # Start background tasks
        receiver_task = asyncio.create_task(self.message_receiver())
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        cli_task = asyncio.create_task(self.cli_control_panel())
        
        # Wait for any task to complete
        done, pending = await asyncio.wait(
            [receiver_task, heartbeat_task, cli_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
        
        # Close connection
        if self.websocket:
            await self.websocket.close()
        
        print("👋 Simulator stopped")


async def main():
    if len(sys.argv) < 3:
        print("Usage: python ocpp_simulator.py <charge_point_id> <central_system_url>")
        print("Example: python ocpp_simulator.py CP001 ws://localhost:9000")
        sys.exit(1)
    
    charge_point_id = sys.argv[1]
    central_system_url = sys.argv[2]
    
    charge_point = OCPP16ChargePoint(charge_point_id, central_system_url)
    await charge_point.run()


if __name__ == "__main__":
    asyncio.run(main())
