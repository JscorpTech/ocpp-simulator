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
- ✅ Har 5 sekundda MeterValues yuboradi (tok, kuchlanish, quvvat, SoC)

## 4️⃣ CLI Buyruqlar

Simulator ishlab turgan vaqtda:

```bash
>>> info                    # Holat ko'rish
>>> status charging         # Status o'zgartirish
>>> current 32              # Tokni 32A ga o'rnatish
>>> current 3600            # Ultra tez charging (1 min = 100%)
>>> soc 20                  # Battery zaryadi 20% ga o'rnatish
>>> autostop off            # Avtomatik to'xtatishni o'chirish
>>> verbose on              # OCPP messagelarni ko'rish
>>> stop                    # Transaction to'xtatish
>>> quit                    # Chiqish
```

## 5️⃣ Charging tezligi

**Default (16A):**
- Power: ~3,680W
- 0% → 100%: ~815 minut (~13.5 soat)

**Fast charging (32A):**
- Power: ~7,360W
- 0% → 100%: ~408 minut (~6.8 soat)

**Ultra fast (100A):**
- Power: ~23,000W
- 0% → 100%: ~130 minut (~2.2 soat)

**1 daqiqada to'lish uchun:**
```bash
>>> soc 0              # 0% dan boshlash
>>> current 3600       # 3600A kiritish
>>> start USER001      # ~1 daqiqada 100% ga yetadi
```

**Hisob-kitob:**
- Battery: 50 kWh (50,000 Wh)
- 1 daqiqada to'lish: 50,000 Wh / (1/60) soat = 3,000,000 W = 3 MW
- Kerakli tok: 3,000,000W / 230V = ~13,043 A (nazariy)
- Amalda: `current 3600` (~10 minut) yoki `current 600` (~1 soat)

## 6️⃣ Charging ma'lumotlari

Charging paytida avtomatik yuboriladi:

```
⚡ Meter: 1250Wh | Current: 16.23A | Power: 3732.90W | Battery: 35.5%
```

- **Current (Tok)**: 16A (o'zgaradi)
- **Voltage (Kuchlanish)**: 230V
- **Power (Quvvat)**: Current × Voltage
- **Battery SoC**: Batareya zaryadi foizi
- **Energy (Energiya)**: Wh (ortib boradi)

## 📝 Misol

```bash
$ python ocpp_simulator.py CP001 ws://localhost:9000
🔌 Connecting to Central System: ws://localhost:9000/CP001
✅ Connected to Central System
📊 Status changed: Available

>>> soc 20                 # 20% dan boshlash
🔋 Battery SoC set to 20.0%

>>> current 200            # Tez charging
⚡ Current set to 200.0A
   Power: 46000.0W
   Time to full from 20.0%: 52.2 minutes

>>> 
# RemoteStartTransaction keladi
🚀 RemoteStartTransaction received for connector 1, idTag: USER001
📊 Status changed: Preparing
📊 Status changed: Charging
🔋 Charging started: 200.0A @ 230.0V = 46000.0W | Battery: 20.0%
   Auto-stop at 100%: Enabled
   Estimated time to full: 52.2 minutes (at current 200.0A)

⚡ Meter: 64Wh | Current: 200.23A | Power: 46052.90W | Battery: 20.1%
⚡ Meter: 128Wh | Current: 199.87A | Power: 45970.10W | Battery: 20.3%
...
⚡ Meter: 40000Wh | Current: 40.45A | Power: 9303.50W | Battery: 100.0%
🔋 Battery full (100%) - auto stopping charge
✅ Transaction stopped successfully
```

## 🎯 Asosiy xususiyatlar

1. **Real charging simulation**: Current ga bog'liq tez/sekin charging
2. **Auto-stop at 100%**: Batareya to'lganda avtomatik to'xtaydi
3. **Time estimation**: Qancha vaqtda to'lishini ko'rsatadi
4. **Flexible testing**: Har qanday current va SoC o'rnatish mumkin
5. **OCPP 1.6 to'liq**: Haqiqiy charging station kabi ishlaydi

Omad! 🎉

