# OCPP 1.6 Charging Station Simulator

Bu simulator OCPP 1.6 protokoli bilan ishlaydigan haqiqiy zaryadlash stansiyadek ishlaydi.

## Xususiyatlari

✅ **Avtomatik Transaction Management**
- RemoteStartTransaction qabul qilinganda avtomatik ravishda:
  - Status: Available → Preparing → Charging
  - StartTransaction yuboradi
  - Charging jarayonini boshlaydi

✅ **Real-time Charging Data**
- Har 10 sekundda MeterValues yuboradi
- Haqiqiy tok (Current), kuchlanish (Voltage), quvvat (Power) ma'lumotlari
- Energiya o'lchagichi (Wh)

✅ **CLI Control Panel**
- Status o'zgartirish
- Error code belgilash
- Qo'lda transaction boshlash/to'xtatish
- Charging tok qiymatini o'zgartirish

## O'rnatish

```bash
pip install -r requirements.txt
```

## Ishlatish

```bash
python ocpp_simulator.py <charge_point_id> <central_system_url>
```

### Misol:

```bash
python ocpp_simulator.py CP001 ws://localhost:9000
```

yoki

```bash
python ocpp_simulator.py STATION-001 ws://your-server.com:9000
```

## CLI Buyruqlari

Simulator ishga tushgandan so'ng quyidagi buyruqlardan foydalanishingiz mumkin:

### Status o'zgartirish
```
status available       - Available holatga o'tkazish
status preparing       - Preparing holatga o'tkazish
status charging        - Charging holatga o'tkazish
status finishing       - Finishing holatga o'tkazish
status faulted         - Faulted holatga o'tkazish
status unavailable     - Unavailable holatga o'tkazish
```

### Error belgilash
```
error noerror          - Xatolik yo'q
error groundfailure    - Yerga tutashish xatosi
error overcurrent      - Haddan tashqari tok xatosi
error undervoltage     - Past kuchlanish
error overvoltage      - Yuqori kuchlanish
```

### Transaction boshqarish
```
start <idTag>          - Transaction boshlash (masalan: start USER001)
stop                   - Joriy transactionni to'xtatish
```

### Charging parametrlarini o'zgartirish
```
current 16             - Charging tokini 16A ga o'rnatish
current 32             - Charging tokini 32A ga o'rnatish
```

### Ma'lumot ko'rish
```
info                   - Joriy holat haqida ma'lumot
help                   - Yordam
quit                   - Chiqish
```

## Avtomatik ishlash

RemoteStartTransaction kelganda simulator avtomatik ravishda:

1. ✅ Status: Available → Preparing (2 sekund)
2. ✅ StartTransaction yuboradi
3. ✅ Transaction ID qabul qiladi
4. ✅ Status: Preparing → Charging
5. ✅ Har 10 sekundda MeterValues yuboradi:
   - Energy: Wh (energiya o'lchagichi)
   - Current: 16A (tok)
   - Voltage: 230V (kuchlanish)
   - Power: ~3680W (quvvat)

## Charging jarayoni

Charging paytida quyidagi ma'lumotlar yuboriladi:

```
⚡ Meter: 1250Wh | Current: 16.23A | Power: 3732.90W
⚡ Meter: 1260Wh | Current: 15.87A | Power: 3650.10W
⚡ Meter: 1270Wh | Current: 16.41A | Power: 3774.30W
```

- **Tok (Current)**: 16A atrofida, ozgina o'zgaradi (15.5-16.5A)
- **Kuchlanish (Voltage)**: 230V
- **Quvvat (Power)**: Current * Voltage
- **Energiya (Energy)**: Vaqt davomida to'plangan energiya (Wh)

## Misol sessiya

```bash
$ python ocpp_simulator.py CP001 ws://localhost:9000

🔌 Connecting to Central System: ws://localhost:9000/CP001
✅ Connected to Central System
📤 Sending: [2,"uuid...","BootNotification",{...}]
📊 Status changed: Available

============================================================
🎛️  CLI CONTROL PANEL
============================================================
Commands:
  status <status>  - Change status
  start <idTag>    - Start transaction manually
  stop             - Stop current transaction
  current <amps>   - Set charging current (A)
  info             - Show current state
  quit             - Exit simulator
============================================================

>>> 

# RemoteStartTransaction keladi...
📥 Received: [2,"uuid...","RemoteStartTransaction",{"idTag":"USER001"}]
🚀 RemoteStartTransaction received for connector 1, idTag: USER001
📤 Sending: [3,"uuid...",{"status":"Accepted"}]
📊 Status changed: Preparing
📤 Sending: [2,"uuid...","StartTransaction",{...}]
✅ Transaction ID: 12345
📊 Status changed: Charging
🔋 Charging started: 16.0A @ 230.0V = 3680.0W
✅ Transaction 12345 started successfully

# Har 10 sekundda:
⚡ Meter: 10Wh | Current: 16.23A | Power: 3732.90W
⚡ Meter: 20Wh | Current: 15.87A | Power: 3650.10W
⚡ Meter: 31Wh | Current: 16.41A | Power: 3774.30W

>>> info
📊 Current State:
  Status: Charging
  Transaction ID: 12345
  ID Tag: USER001
  Meter: 125 Wh
  Current: 16.23 A
  Voltage: 230.00 V
  Power: 3732.90 W
  Charging: True

>>> current 32
⚡ Current set to 32.0A, Power: 7360.0W

>>> stop
🛑 Stopping transaction...
📊 Status changed: Finishing
📤 Sending: [2,"uuid...","StopTransaction",{...}]
📊 Status changed: Available
✅ Transaction stopped successfully
```

## Test qilish

1. Central System serveringizni ishga tushiring
2. Simulator ishga tushiring
3. Central System'dan RemoteStartTransaction yuboring
4. Simulator avtomatik ravishda transaction boshlaydi va charging ma'lumotlarini yuboradi

## Muammolar

Agar muammo yuzaga kelsa:

1. Central System URL to'g'ri ekanligini tekshiring
2. WebSocket ulanish ochiq ekanligini tekshiring
3. OCPP 1.6 subprotocol qo'llab-quvvatlanishini tekshiring

## Litsenziya

MIT License
