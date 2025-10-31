# 🚀 OCPP 1.6 Simulator - Tezkor Boshlash

## 1️⃣ O'rnatish

```bash
pip install websockets aioconsole
```

yoki

```bash
pip install -r requirements.txt
```

## 2️⃣ Ishga tushirish

### Oddiy usul:
```bash
python ocpp_simulator.py CP001 ws://localhost:9000
```

### Script orqali:
```bash
./run_simulator.sh CP001 ws://localhost:9000
```

## 3️⃣ RemoteStartTransaction test

Simulator ishga tushgandan keyin, Central System'dan quyidagi OCPP message yuboring:

```json
[
  2,
  "unique-id-123",
  "RemoteStartTransaction",
  {
    "connectorId": 1,
    "idTag": "USER001"
  }
]
```

Simulator avtomatik:
- ✅ Status: Preparing
- ✅ StartTransaction yuboradi
- ✅ Status: Charging
- ✅ Har 10 sekundda MeterValues yuboradi (tok, kuchlanish, quvvat)

## 4️⃣ CLI Buyruqlar

Simulator ishlab turgan vaqtda:

```bash
>>> info                    # Holat ko'rish
>>> status charging         # Status o'zgartirish
>>> current 32              # Tokni 32A ga o'rnatish
>>> stop                    # Transaction to'xtatish
>>> quit                    # Chiqish
```

## 5️⃣ Charging ma'lumotlari

Charging paytida avtomatik yuboriladi:

```
⚡ Meter: 1250Wh | Current: 16.23A | Power: 3732.90W
```

- **Current (Tok)**: 16A (o'zgaradi)
- **Voltage (Kuchlanish)**: 230V
- **Power (Quvvat)**: ~3680W
- **Energy (Energiya)**: Wh (ortib boradi)

## 📝 Misol

```bash
$ python ocpp_simulator.py CP001 ws://localhost:9000
🔌 Connecting to Central System: ws://localhost:9000/CP001
✅ Connected to Central System
📊 Status changed: Available

>>> 
# RemoteStartTransaction keladi
🚀 RemoteStartTransaction received for connector 1, idTag: USER001
📊 Status changed: Preparing
📊 Status changed: Charging
🔋 Charging started: 16.0A @ 230.0V = 3680.0W
⚡ Meter: 10Wh | Current: 16.23A | Power: 3732.90W

>>> info
📊 Current State:
  Status: Charging
  Transaction ID: 12345
  Meter: 125 Wh
  Current: 16.23 A
  Power: 3732.90 W
  Charging: True
```

## 🎯 Asosiy xususiyatlar

1. **Avtomatik transaction**: RemoteStartTransaction qabul qilganda o'zi hamma narsani avtomatik qiladi
2. **Real-time data**: Charging paytida har 10 sekundda tok, kuchlanish, quvvat yuboradi
3. **CLI boshqaruv**: Status, error, current qo'lda o'zgartirish mumkin
4. **OCPP 1.6 to'liq**: Haqiqiy charging station kabi ishlaydi

Omad! 🎉
