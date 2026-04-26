# Battytrade Smart Trading Dashboard

ระบบต้นแบบสำหรับวิเคราะห์และแสดงสัญญาณเทรดแบบรวมศูนย์ (หุ้นไทย, หุ้นสหรัฐ, Forex Spot) พร้อมแดชบอร์ดสวยงาม ใช้งานผ่านเว็บเบราว์เซอร์

## ความสามารถหลัก
- ดูภาพรวมตลาดไทย/สหรัฐ/Forex แบบ real-time mock stream
- ระบบสร้างสัญญาณ (`BUY` / `SELL` / `HOLD`) ตาม scoring model ที่ปรับแต่งได้
- วิเคราะห์ความเสี่ยงก่อนส่งคำสั่ง (Risk Gate)
- Dashboard เดียวรวม watchlist, top signals, และ market heat

> หมายเหตุ: เวอร์ชันนี้เป็น **Prototype** เพื่อช่วยวางโครงสร้างระบบการเทรดเท่านั้น ยังไม่เชื่อมต่อโบรกเกอร์จริง

## เริ่มต้นใช้งาน
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

เปิด: `http://127.0.0.1:8000`

## API หลัก
- `GET /api/watchlist` - ดึงรายการสินทรัพย์ที่ติดตาม
- `GET /api/signals` - ดึงสัญญาณที่คำนวณแล้ว
- `GET /api/analysis/{symbol}` - วิเคราะห์เชิงลึกก่อนเข้าเทรด
- `GET /api/market-summary` - สรุปภาพรวมตลาด

## สถาปัตยกรรม
- **FastAPI**: API + static dashboard
- **Signal Engine**: คำนวณ score จาก momentum/volatility/trend/liquidity
- **Risk Analyzer**: ประเมิน stop-loss/take-profit และความเสี่ยงเชิงสัดส่วน
- **Frontend Dashboard**: HTML/CSS/JS responsive, modern UI

