# VarbaraF2EMA - FutureBot EMA Cross - V.1.1 + HEDGE MODE Mod by X48151623442
  Update วันที่ 25/08/2565
    - เพิ่ม params สำหรับ Hedge Mode เพื่อให้ใช้ได้ร่วมกับ OneWay Mode เดิม

# Var Setting
_ใน Var Setting ส่วนประกอบหลักๆที่ต้องมีดังนี้_
  1. API_KEY
  2. API_SECRET
  3. BOT_NAME
  4. COST_PERCENT
  5. FAST_EMAVALUE
  6. LEVERAGE_X
  7. LINE_TOKEN
  8. MODE
  9. ORDER_ENABLE
  10. SLOW_EMAVALUE
  11. SL_PERCENT
  12. SYMBOL_NAME
  13. TF
  14. TP_PERCENT
  15. USER_BOT

# ขั้นตอนการใช้งาน
  1. เพิ่ม API + SECRET + LINE TOKEN ให้เรียบร้อย
  2. กำหนด COST %
  3. กำหนดค่า EMA FAST / EMA SLOW
  4. กำหนด LEVERAGE ต้องใช้ , คั่น หากมีหลายคู่เทรด
  5. Mode = on
    5.1 หาก off จะยกเลิกการ TP/SL
    5.2 หาก on จะเป็นการเปิดใช้งาน TP/SL ตาม % ที่ตั้งใว้
  6. ORDER_ENABLE
    6.1 หาก TRUE จะเป็นการเปิดใช้งานชุดคำสั่งทั้งหมด
    6.2 หาก FALSE ปิดระบบ ไม่รับสัญญาณ
  7. กำหนดค่า TP/SL
  8. กำหนด SYMBOL_NAME โดยการใช้ , (comma) คั่นหากมีคู่เทรด 2 คู่ขึ้นไป
  9. TF (ปัจจุบันเลือกได้ 1 TF ต่อการรัน 1 ชุด รอปรับปรุงพัฒนาในรุ่นต่อไปเพื่อแยก TF)
  10. Deploy และรอสถานะ

# การตรวจสอบสถานะการใช้งาน
  1. Status : Wait Position....
        หมายถึง รอสัญญาณ EMA Cross หากได้รับสัญญาณ จะเปลี่ยนสถานะใหม่
  2. Status  : Short Position
        หมายถึง รับสัญญาณ Short และเปิด Position แล้ว
  3. Status : Long Position
        หมายถึง : รับสัญญาณ Long และเปิด Position แล้ว
