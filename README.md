# 🧪 Universal Kimyo & Matematika Kalkulyatori Boti

Telegramda kimyoviy tenglamalarni tenglashtirish, moddalarning molyar massasini hisoblash, stexiometriya, eritmalar va interaktiv matematik hisob-kitoblarni amalga oshiruvchi bot.

---

## 🌟 Imkoniyatlari

### 1. ⚖️ Kimyoviy Reaksiyalarni Tenglashtirish (Balancer)
- Istalgan kimyoviy reaksiyani chatga yuboring, bot Gauss-Jordan algoritmi yordamida stexiometrik koeffitsiyentlarni aniqlaydi:
  - `H2 + O2 = H2O` $\rightarrow$ `2H2 + O2 = 2H2O`
  - `KMnO4 + HCl = KCl + MnCl2 + Cl2 + H2O` $\rightarrow$ `2KMnO4 + 16HCl = 2KCl + 2MnCl2 + 5Cl2 + 8H2O`
  - `C2H6 + O2 -> CO2 + H2O` $\rightarrow$ `2C2H6 + 7O2 = 4CO2 + 6H2O`
  - `Fe + Cl2 = FeCl3` $\rightarrow$ `2Fe + 3Cl2 = 2FeCl3`

### 2. 🧪 Molyar Massa ($M_r$) va Elementlar Foiz Tarkibi
- Oddiy va murakkab formulalar, qavsli birikmalar va kristallogidratlarni to'liq qo'llab-quvvatlaydi:
  - `H2SO4` $\rightarrow$ $98.072 \text{ g/mol}$ (H: 2.06%, S: 32.69%, O: 65.25%)
  - `Ca(OH)2` $\rightarrow$ $74.092 \text{ g/mol}$
  - `CuSO4*5H2O` (kristallogidrat) $\rightarrow$ $249.677 \text{ g/mol}$
  - `K4[Fe(CN)6]` $\rightarrow$ $368.345 \text{ g/mol}$

### 3. 📊 Stexiometriya va Modda Miqdori ($n, m, V, N$)
- Mol, massa, hajm va molekulalar soni:
  - Masalan chatga: `36g H2O` yozsangiz $\rightarrow$ $n = 2 \text{ mol}$, $V = 44.8 \text{ L}$, $N = 1.20 \times 10^{24} \text{ ta}$.

### 4. 💧 Eritmalar Konsentratsiyasi ($w\%$)
- Moddaning massa ulushi va erituvchi (suv) massalari nisbati:
  - Masalan chatga: `20g tuz + 80g suv` yozsangiz $\rightarrow$ $\omega = 20\%$, $m_{\text{eritma}} = 100 \text{ g}$.

### 5. ⚛️ Mendeleyev Davriy Jadvali (118 ta element)
- Istalgan element haqida ma'lumot olish:
  - `/elem Fe` yoki `/elem Temir` yoki `/elem 26`
  - Atom raqami, nisbiy atom massasi, davri va guruhi.

### 6. 🧮 Interaktiv Matematik Kalkulyator
- Tugmali interaktiv klaviatura (`/calc`).
- Matnli arifmetik amallar: `15000 * 4 + 10%`.
- Amallar tarixi (`📜 Tarix`).

---

## 🚀 Ishga tushirish (Qadamma-qadam)

### 1. Tokenni sozlash
`calculator_bot/.env` fayliga tokenni kiriting:
```env
CALCULATOR_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r calculator_bot/requirements.txt
```

### 3. Botni ishga tushirish
```bash
python calculator_bot/bot.py
```

### 4. Railway'da Deploy qilish
1. GitHub'ga o'zgarishlarni `git push` qiling.
2. Railway loyihangizning **Variables** bo'limiga o'ting.
3. `CALCULATOR_BOT_TOKEN` nomli o'zgaruvchi yaratib, bot tokeningizni kiriting.
4. Deploy avtomatik ishga tushadi!
