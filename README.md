# 🧮 Telegram Interaktiv Kalkulyator Boti

Ushbu bot Telegramda bevosita tugmalar orqali yoki chatga matnli ifodalar yozish orqali hisoblash imkonini beruvchi zamonaviy bot hisoblanadi.

---

## 🌟 Imkoniyatlari

1. **Interaktiv Tugmali Kalkulyator:**
   - 0 dan 9 gacha raqamlar
   - Asosiy amallar: `+`, `−`, `×`, `÷`, `%`, `(`, `)`
   - Displeyni tozalash (`🧹 C`) va oxirgi raqamni o'chirish (`⌫`)
   - Natijani chiqarish (`🟰 Teng`)
2. **Xavfsiz Matematik Parser:**
   - Standart xavfli `eval()` o'rniga Python `ast` daraxti orqali hisoblaydi.
   - Nolga bo'lish va noaniq ifodalarni avtomatik tutadi.
3. **Chatdan to'g'ridan-to'g'ri hisoblash:**
   - Istalgan matematik ifodani chatga yozib yuboring:
     - `15000 * 4`
     - `500 + 15%`
     - `(1000000 - 250000) / 5`
     - `2 ^ 8`
4. **Hisob-kitoblar Tarixi:**
   - Oxirgi hisoblangan 10 ta amal xotirada saqlanadi (`/history` yoki `📜 Tarix` tugmasi).

---

## 🚀 Ishga tushirish (Qadamma-qadam)

### 1. Bot tokenini olish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botga nom va `@calculator...bot` shaklida username bering.
4. BotFather bergan **API Token**ni nusxalab oling (masalan: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

### 2. Tokenni sozlash
`calculator_bot/` jildida `.env` fayl yarating (yoki `.env.example` dan nusxa oling) va tokenni yozing:

```env
CALCULATOR_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r calculator_bot/requirements.txt
```

### 4. Botni ishga tushirish
```bash
python calculator_bot/bot.py
```

Endi botingizga kirib `/start` bosing va hisoblashni boshlang!
