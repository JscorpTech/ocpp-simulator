#!/bin/bash

# OCPP 1.6 Simulator Runner Script

# Default values
CHARGE_POINT_ID="${1:-CP001}"
CENTRAL_SYSTEM_URL="${2:-ws://localhost:9000}"

echo "🚀 Starting OCPP 1.6 Charging Station Simulator"
echo "   Charge Point ID: $CHARGE_POINT_ID"
echo "   Central System: $CENTRAL_SYSTEM_URL"
echo ""

python3 ocpp_simulator.py "$CHARGE_POINT_ID" "$CENTRAL_SYSTEM_URL"
