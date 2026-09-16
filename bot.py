"""
Kimyo Kalkulyatori Boti (Aiogram 3)
Kimyoviy tenglamalarni tenglashtirish, Molyar massa (Mr), Elementlar tarkibi,
Stexiometriya, Eritmalar va Interaktiv Matematik Kalkulyator.
"""

import asyncio
import logging
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

# calculator_bot papkasini pathga qo'shish
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculator import SafeMathEvaluator, calculate, format_number
from chemistry import (
    PERIODIC_TABLE,
    balance_equation,
    calculate_molar_mass,
    calculate_solution_mass_fraction,
    calculate_stoichiometry,
    find_element,
    parse_formula,
)
from keyboards import (
    format_calculator_display,
    get_back_keyboard,
    get_calculator_keyboard,
    get_main_menu_keyboard,
    get_quick_balance_keyboard,
    get_quick_mr_keyboard,
)

# .env yuklash
load_dotenv()
BOT_TOKEN = os.getenv("CALCULATOR_BOT_TOKEN") or os.getenv("BOT_TOKEN")

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("chemistry_bot")

# Foydalanuvchilar arifmetik kalkulyator sessiyalari
user_sessions: Dict[int, Dict] = defaultdict(lambda: {
    "expression": "",
    "result": "",
    "just_calculated": False
})
user_history: Dict[int, List[str]] = defaultdict(list)


def add_to_history(user_id: int, item: str) -> None:
    """Arifmetik tarixga yangi yozuv qo'shish (maksimum 10 ta)"""
    history = user_history[user_id]
    history.append(item)
    if len(history) > 10:
        history.pop(0)


dp = Dispatcher()


# ==========================================
# FORMATLASH YORDAMCHILARI (HTML FORMATTERS)
# ==========================================

def format_mr_message(res: dict) -> str:
    """Molyar massa natijasini chiroyli HTML qilib formatlash"""
    formula = res["formula"]
    total = res["total_mass"]
    elements = res["elements"]

    lines = [
        f"🧪 <b>Modda:</b> <code>{formula}</code>",
        f"⚖️ <b>Molyar massa (Mr):</b> <code>{total:.3f} g/mol</code>",
        "━━━━━━━━━━━━━━━━━━━━",
        "📊 <b>Elementlar bo'yicha tarkib:</b>",
    ]

    for el in elements:
        sym = el["symbol"]
        name = el["name"]
        cnt = el["count"]
        m_tot = el["total_mass"]
        w = el["fraction"]
        lines.append(
            f"• <b>{sym}</b> ({name}): <code>{cnt} ta</code> | <code>{m_tot:.2f} g/mol</code> (<b>{w:.2f}%</b>)"
        )

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 <i>Boshqa formula hisoblash uchun uni chatga yozib yuboring (masalan: <code>Ca(OH)2</code>).</i>")
    return "\n".join(lines)


def format_balance_message(orig: str, balanced: str, react_info: list, prod_info: list) -> str:
    """Tenglashtirilgan reaksiya xabarini formatlash"""
    lines = [
        "⚖️ <b>Kimyoviy Reaksiya Tenglashtirildi!</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        f"📝 <b>Boshlang'ich:</b> <code>{orig}</code>",
        f"🎯 <b>Natija:</b>",
        f"👉 <b><code>{balanced}</code></b>",
        "━━━━━━━━━━━━━━━━━━━━",
        "🔍 <b>Stexiometrik koeffitsiyentlar:</b>",
    ]

    lines.append("🔹 <b>Reagentlar:</b>")
    for mol, coef in react_info:
        lines.append(f"   • <b>{coef}</b> ta <code>{mol}</code>")

    lines.append("🔸 <b>Mahsulotlar:</b>")
    for mol, coef in prod_info:
        lines.append(f"   • <b>{coef}</b> ta <code>{mol}</code>")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 <i>Istalgan reaksiyani chatga yozing (masalan: <code>Fe + Cl2 = FeCl3</code>).</i>")
    return "\n".join(lines)


def format_element_message(el: dict) -> str:
    """Davriy jadval elementi kartochkasi"""
    return (
        f"⚛️ <b>Kimyoviy Element: {el['name']} ({el['symbol']})</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🔢 <b>Tartib raqami (Z):</b> <code>{el['number']}</code>\n"
        f"⚖️ <b>Nisbiy atom massasi (Ar):</b> <code>{el['mass']} g/mol</code>\n"
        f"📅 <b>Davr:</b> <code>{el['period']}</code>\n"
        f"🏛 <b>Guruh:</b> <code>{el['group']}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Qidiruv uchun element belgisi, raqami yoki nomini yozing (masalan: <code>Fe</code>, <code>26</code>, <code>Temir</code>).</i>"
    )


# ==========================================
# BUYRUQLAR (COMMAND HANDLERS)
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """
    /start buyrug'i - asosiy kimyo kalkulyatori menyusi
    """
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "Men <b>Universal Kimyo & Matematika Kalkulyatori</b> botiman 🧪🧮\n\n"
        "<b>Mening imkoniyatlarim:</b>\n"
        "⚖️ <b>Reaksiyalarni tenglashtirish:</b> <code>H2 + O2 = H2O</code>\n"
        "🧪 <b>Molyar massa (Mr) & foiz tarkib:</b> <code>H2SO4</code> yoki <code>CuSO4*5H2O</code>\n"
        "📊 <b>Stexiometriya:</b> mol, massa, hajm, zarrachalar\n"
        "💧 <b>Eritmalar:</b> massa ulush (w%), konsentratsiyalar\n"
        "⚛️ <b>Davriy jadval:</b> 118 ta element ma'lumotnomasi\n"
        "🧮 <b>Arifmetik kalkulyator:</b> qulay tugmali interfeys\n\n"
        "<i>Quyidagi menyudan kerakli bo'limni tanlang yoki to'g'ridan-to'g'ri formula/tenglama yuboring:</i>"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.HTML)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """
    /help - foydalanish bo'yicha to'liq qo'llanma
    """
    help_text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "<b>1. Kimyoviy tenglamalarni tenglashtirish:</b>\n"
        "Reaksiyani chatga yozing, masalan:\n"
        "• <code>KMnO4 + HCl = KCl + MnCl2 + Cl2 + H2O</code>\n"
        "• <code>C2H6 + O2 = CO2 + H2O</code>\n"
        "• <code>Fe + Cl2 -> FeCl3</code>\n\n"
        "<b>2. Molyar massani hisoblash (Mr):</b>\n"
        "Formulani chatga yozing:\n"
        "• <code>H2SO4</code>\n"
        "• <code>Ca(OH)2</code>\n"
        "• <code>CuSO4*5H2O</code> (kristallogidrat)\n"
        "• <code>K4[Fe(CN)6]</code>\n\n"
        "<b>3. Davriy jadvaldan element qidirish:</b>\n"
        "• <code>/elem Fe</code> yoki <code>/elem 26</code> yoki <code>/elem Oltin</code>\n\n"
        "<b>4. Arifmetik hisoblash:</b>\n"
        "• <code>/calc</code> buyrug'i yoki istalgan amal: <code>1500 * 4 + 10%</code>\n\n"
        "<b>5. Stexiometriya va Eritmalar:</b>\n"
        "Quyidagi tugmalar orqali menyuga o'ting:"
    )
    await message.answer(help_text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.HTML)


@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    """
    /balance buyrug'i - reaksiya tenglashtirish
    """
    args = message.text[len("/balance"):].strip()
    if args:
        success, res, r_info, p_info = balance_equation(args)
        if success:
            await message.answer(format_balance_message(args, res, r_info, p_info), parse_mode=ParseMode.HTML)
        else:
            await message.answer(f"⚠️ <b>Xatolik:</b> {res}", parse_mode=ParseMode.HTML)
    else:
        text = (
            "⚖️ <b>Kimyoviy Reaksiyalarni Tenglashtirish</b>\n\n"
            "Tenglashtirmoqchi bo'lgan reaksiyangizni chatga yozing:\n"
            "Masalan: <code>Al + H2SO4 = Al2(SO4)3 + H2</code>\n\n"
            "Yoki quyidagi mashhur namunalardan birini sinab ko'ring:"
        )
        await message.answer(text, reply_markup=get_quick_balance_keyboard(), parse_mode=ParseMode.HTML)


@dp.message(Command("mr"))
async def cmd_mr(message: Message):
    """
    /mr buyrug'i - molyar massa
    """
    args = message.text[len("/mr"):].strip()
    if args:
        success, res = calculate_molar_mass(args)
        if success:
            await message.answer(format_mr_message(res), parse_mode=ParseMode.HTML)
        else:
            await message.answer(f"⚠️ <b>Xatolik:</b> {res}", parse_mode=ParseMode.HTML)
    else:
        text = (
            "🧪 <b>Molyar massa (Mr) & Elementlar tarkibi</b>\n\n"
            "Formulani yozib yuboring (masalan: <code>H3PO4</code>, <code>Ca(OH)2</code>, <code>CuSO4*5H2O</code>):\n\n"
            "Yoki namunalardan birini tanlang:"
        )
        await message.answer(text, reply_markup=get_quick_mr_keyboard(), parse_mode=ParseMode.HTML)


@dp.message(Command("elem"))
async def cmd_elem(message: Message):
    """
    /elem buyrug'i - davriy jadval elementi
    """
    query = message.text[len("/elem"):].strip()
    if not query:
        await message.answer(
            "Iltimos, element belgisi, nomi yoki tartib raqamini kiriting.\nMasalan: <code>/elem Fe</code> yoki <code>/elem 79</code>",
            parse_mode=ParseMode.HTML
        )
        return

    el = find_element(query)
    if el:
        await message.answer(format_element_message(el), parse_mode=ParseMode.HTML)
    else:
        await message.answer(f"⚠️ '<b>{query}</b>' bo'yicha element topilmadi.", parse_mode=ParseMode.HTML)


@dp.message(Command("calc"))
async def cmd_calc(message: Message):
    """
    /calc - interaktiv arifmetik kalkulyator
    """
    user_id = message.from_user.id
    user_sessions[user_id] = {
        "expression": "",
        "result": "",
        "just_calculated": False
    }
    display = format_calculator_display(expression="", result="")
    await message.answer(display, reply_markup=get_calculator_keyboard(), parse_mode=ParseMode.HTML)


# ==========================================
# CALLBACK QUERY HANDLERS (INLINE TUGMALAR)
# ==========================================

@dp.callback_query(F.data.startswith("chem:"))
async def on_chem_callback(callback: CallbackQuery):
    data = callback.data

    if data == "chem:menu:main":
        text = (
            "🧪 <b>Universal Kimyo & Matematika Boti</b>\n"
            "Kerakli bo'limni tanlang yoki to'g'ridan-to'g'ri formula/reaksiyani chatga yozing:"
        )
        await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    if data == "chem:menu:balance":
        text = (
            "⚖️ <b>Reaksiyalarni Tenglashtirish Bo'limi</b>\n\n"
            "Tenglashtirmoqchi bo'lgan reaksiyangizni chatga yozing.\n"
            "<i>Masalan: <code>KMnO4 + HCl = KCl + MnCl2 + Cl2 + H2O</code></i>\n\n"
            "Yoki quyidagi namunalardan birini bosing:"
        )
        await callback.message.edit_text(text, reply_markup=get_quick_balance_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    if data == "chem:menu:mr":
        text = (
            "🧪 <b>Molyar massa (Mr) & Elementlar tarkibi</b>\n\n"
            "Kimyoviy modda formulasini chatga yozing.\n"
            "<i>Masalan: <code>H2SO4</code>, <code>Ca(OH)2</code>, <code>CuSO4*5H2O</code></i>\n\n"
            "Yoki namunalardan birini tanlang:"
        )
        await callback.message.edit_text(text, reply_markup=get_quick_mr_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    if data == "chem:menu:stechio":
        text = (
            "📊 <b>Stexiometriya va Modda Miqdori (n, m, V, N)</b>\n\n"
            "Asosiy formulalar:\n"
            "• <b>Mol miqdori:</b> <code>n = m / M</code>\n"
            "• <b>Gazlar hajmi (n.sh.):</b> <code>V = n × 22.4 L</code>\n"
            "• <b>Zarrachalar soni:</b> <code>N = n × 6.022·10²³</code>\n\n"
            "💡 <i>Hisoblash uchun chatga quyidagicha yozishingiz mumkin:\n"
            "Masalan: <code>36g H2O</code> yoki <code>2mol CO2</code> yoki <code>44.8L O2</code></i>"
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    if data == "chem:menu:solution":
        text = (
            "💧 <b>Eritmalar Konsentratsiyasi (w%)</b>\n\n"
            "Asosiy formulalar:\n"
            "• <b>Massa ulush:</b> <code>w% = (m_erigan / m_eritma) × 100%</code>\n"
            "• <code>m_eritma = m_erigan + m_suv</code>\n\n"
            "💡 <i>Chatga qiymatlarni yozishingiz mumkin:\n"
            "Masalan: <code>20g tuz + 80g suv</code> yoki <code>25g modda 100g eritma</code></i>"
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    if data == "chem:menu:element":
        text = (
            "⚛️ <b>Mendeleyev Davriy Jadvali (118 ta element)</b>\n\n"
            "Istalgan element haqida ma'lumot olish uchun uning <b>belgisini</b>, <b>nomini</b> yoki <b>tartib raqamini</b> yozing:\n\n"
            "Misollar:\n"
            "• <code>Fe</code> yoki <code>Temir</code> yoki <code>26</code>\n"
            "• <code>Au</code> yoki <code>Oltin</code> yoki <code>79</code>\n"
            "• <code>U</code> yoki <code>Uran</code> yoki <code>92</code>"
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    if data == "chem:menu:calc":
        user_id = callback.from_user.id
        user_sessions[user_id] = {"expression": "", "result": "", "just_calculated": False}
        display = format_calculator_display(expression="", result="")
        await callback.message.edit_text(display, reply_markup=get_calculator_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    if data == "chem:menu:help":
        help_text = (
            "📖 <b>Botdan to'liq foydalanish imkoniyatlari:</b>\n\n"
            "1️⃣ <b>Reaksiyalarni tenglashtirish:</b> Istalgan reaksiya tenglamasini chatga tashlang.\n"
            "2️⃣ <b>Molyar massa:</b> Formulani kiriting (masalan <code>H2SO4</code>), bot elementlar foizigacha chiqaradi.\n"
            "3️⃣ <b>Element qidirish:</b> Element nomi yoki raqamini yozing (<code>Fe</code>, <code>26</code>).\n"
            "4️⃣ <b>Oddiy kalkulyator:</b> Matematik misollarni bevosita hisoblaydi."
        )
        await callback.message.edit_text(help_text, reply_markup=get_back_keyboard(), parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    # Tezkor misollar: chem:eq:...
    if data.startswith("chem:eq:"):
        eq = data[len("chem:eq:"):]
        success, res, r_info, p_info = balance_equation(eq)
        if success:
            await callback.message.answer(format_balance_message(eq, res, r_info, p_info), parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(f"⚠️ {res}", parse_mode=ParseMode.HTML)
        await callback.answer()
        return

    # Tezkor misollar: chem:mr:...
    if data.startswith("chem:mr:"):
        formula = data[len("chem:mr:"):]
        success, res = calculate_molar_mass(formula)
        if success:
            await callback.message.answer(format_mr_message(res), parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(f"⚠️ {res}", parse_mode=ParseMode.HTML)
        await callback.answer()
        return


# ==========================================
# ARIFMETIK INTERAKTIV KALKULYATOR CALLBACKS
# ==========================================

@dp.callback_query(F.data.startswith("calc:"))
async def on_calc_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    action = callback.data[5:]
    session = user_sessions[user_id]
    current_expr = session["expression"]

    # 1. Tozalash (C)
    if action == "clear":
        session["expression"] = ""
        session["result"] = ""
        session["just_calculated"] = False

    # 2. Bitta o'chirish (Backspace)
    elif action == "back":
        if session["just_calculated"]:
            session["expression"] = ""
            session["result"] = ""
            session["just_calculated"] = False
        elif current_expr:
            session["expression"] = current_expr[:-1]

    # 3. Tugma bosilishi (btn:X)
    elif action.startswith("btn:"):
        char = action[4:]
        if session["just_calculated"]:
            if char in ("+", "−", "×", "÷", "%"):
                session["expression"] = (session["result"] or current_expr) + char
            else:
                session["expression"] = char
            session["result"] = ""
            session["just_calculated"] = False
        else:
            session["expression"] += char

    # 4. Hisoblash (Teng)
    elif action == "equals":
        if current_expr:
            success, raw_res, formatted = calculate(current_expr)
            if success:
                add_to_history(user_id, f"{current_expr} = {formatted}")
                session["result"] = formatted
                session["just_calculated"] = True
            else:
                try:
                    display = format_calculator_display(expression=current_expr, error=raw_res)
                    await callback.message.edit_text(display, reply_markup=get_calculator_keyboard(), parse_mode=ParseMode.HTML)
                except TelegramBadRequest:
                    pass
                await callback.answer(f"Xatolik: {raw_res}", show_alert=True)
                return

    # 5. Tarix
    elif action == "history":
        hist = user_history[user_id]
        if not hist:
            await callback.answer("📜 Hali hisoblashlar tarixi mavjud emas.", show_alert=True)
            return
        hist_text = "📜 <b>Oxirgi hisob-kitoblar tarixi:</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        hist_text += "\n".join(f"• <code>{item}</code>" for item in reversed(hist))
        await callback.answer()
        await callback.message.answer(hist_text, parse_mode=ParseMode.HTML)
        return

    display = format_calculator_display(expression=session["expression"], result=session["result"])
    try:
        await callback.message.edit_text(display, reply_markup=get_calculator_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        pass
    await callback.answer()


# ==========================================
# SMART MATN HANDLER (MESSAGE ROUTER)
# ==========================================

@dp.message()
async def handle_any_message(message: Message):
    """
    Intellektual xabar yo'naltiruvchisi:
    1. Agar '=' yoki '->' bo'lsa -> Reaksiya tenglashtirish
    2. Agar Stexiometriya shabloniga tushsa -> Stexiometriya
    3. Agar Eritma shabloniga tushsa -> Eritmalar konsentratsiyasi
    4. Agar Davriy jadval elementi bo'lsa -> Element kartochkasi
    5. Agar Kimyoviy formula bo'lsa -> Molyar massa (Mr)
    6. Aks holda Matematik hisoblash!
    """
    text = message.text.strip()
    user_id = message.from_user.id

    # 1. Kimyoviy reaksiya tenglamasi tekshiruvi (=, ->, =>, ⇌)
    if any(sep in text for sep in ("=", "->", "=>", "⇌", "⇄")):
        success, res, r_info, p_info = balance_equation(text)
        if success:
            await message.answer(format_balance_message(text, res, r_info, p_info), parse_mode=ParseMode.HTML)
            return
        else:
            await message.answer(
                f"⚠️ <b>Reaksiyani tenglashtirishda xatolik:</b>\n{res}\n\n"
                "<i>Namuna: <code>KMnO4 + HCl = KCl + MnCl2 + Cl2 + H2O</code></i>",
                parse_mode=ParseMode.HTML
            )
            return

    # 2. Stexiometriya intellektual aniqlash: masalan "36g H2O" yoki "2 mol CO2" yoki "44.8l O2"
    stechio_match = re.match(r"^([\d\.]+)\s*(g|gr|mol|l|litr)\s+([A-Za-z0-9\(\)\[\]\*\.]+)", text, re.IGNORECASE)
    if stechio_match:
        val = float(stechio_match.group(1))
        unit = stechio_match.group(2).lower()
        form = stechio_match.group(3)

        mass_val = val if unit in ("g", "gr") else None
        mol_val = val if unit == "mol" else None
        vol_val = val if unit in ("l", "litr") else None

        try:
            res = calculate_stoichiometry(formula=form, mass=mass_val, moles=mol_val, volume=vol_val)
            resp = (
                f"📊 <b>Stexiometrik hisoblash:</b> <code>{res['formula']}</code>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"⚖️ <b>Molyar massa:</b> <code>{res['molar_mass']} g/mol</code>\n"
                f"🔹 <b>Mol miqdori (n):</b> <code>{res['moles']} mol</code>\n"
                f"🔹 <b>Massasi (m):</b> <code>{res['mass']} g</code>\n"
                f"🔹 <b>Hajmi (V, n.sh.):</b> <code>{res['volume']} L</code>\n"
                f"🔹 <b>Zarrachalar soni (N):</b> <code>{res['particles']} ta</code>\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            await message.answer(resp, parse_mode=ParseMode.HTML)
            return
        except Exception as e:
            await message.answer(f"⚠️ Stexiometriya xatosi: {str(e)}", parse_mode=ParseMode.HTML)
            return

    # 3. Eritma massasi intellektual aniqlash: masalan "20g tuz + 80g suv" yoki "25g modda 100g eritma"
    sol_match = re.match(r"^([\d\.]+)\s*g?\s*\+?\s*([\d\.]+)\s*g?\s*(suv|eritma|tuz)?", text, re.IGNORECASE)
    if "eritma" in text.lower() or "suv" in text.lower() or "%" in text:
        m1 = re.search(r"([\d\.]+)\s*(?:g|gr)?\s*(?:modda|tuz|erigan)?", text, re.IGNORECASE)
        m2 = re.search(r"([\d\.]+)\s*(?:g|gr)?\s*(?:suv|eritma)", text, re.IGNORECASE)
        if m1 and m2:
            try:
                v1 = float(m1.group(1))
                v2 = float(m2.group(1))
                is_sol = "eritma" in text.lower()
                calc_res = calculate_solution_mass_fraction(
                    solute_mass=v1,
                    solution_mass=v2 if is_sol else None,
                    solvent_mass=None if is_sol else v2,
                )
                resp = (
                    "💧 <b>Eritma konsentratsiyasi hisoblandi:</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"🍬 <b>Erigan modda massasi:</b> <code>{calc_res['solute_mass']} g</code>\n"
                    f"💧 <b>Erituvchi (suv) massasi:</b> <code>{calc_res['solvent_mass']} g</code>\n"
                    f"🧪 <b>Umumiy eritma massasi:</b> <code>{calc_res['solution_mass']} g</code>\n"
                    f"🎯 <b>Massa ulushi (w%):</b> <b><code>{calc_res['fraction_percent']}%</code></b>\n"
                    "━━━━━━━━━━━━━━━━━━━━"
                )
                await message.answer(resp, parse_mode=ParseMode.HTML)
                return
            except Exception:
                pass

    # 4. Kimyoviy formula tekshiruvi (H2O, H2SO4, Ca(OH)2, CuSO4*5H2O ...)
    # Bosh harf bilan boshlangan va kimyoviy elementlardan tashkil topgan bo'lsa
    if re.match(r"^[A-Z][a-zA-Z0-9\(\)\[\]\*\·\.]*$", text):
        success, res = calculate_molar_mass(text)
        if success:
            await message.answer(format_mr_message(res), parse_mode=ParseMode.HTML)
            return

    # 5. Element qidirish tekshiruvi (masalan foydalanuvchi "Temir" yoki "Fe" yoki "Oltin" deb yozsa)
    el = find_element(text)
    if el and len(text) <= 15:
        await message.answer(format_element_message(el), parse_mode=ParseMode.HTML)
        return

    # 6. Matematik ifoda tekshiruvi
    has_digits = any(c.isdigit() for c in text)
    if has_digits:
        success, raw_result, formatted = calculate(text)
        if success:
            add_to_history(user_id, f"{text} = {formatted}")
            response_text = (
                "🔢 <b>Matematik hisoblash natijasi:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📝 Ifoda: <code>{text}</code>\n"
                f"🎯 <b>Natija:</b> <code>{formatted}</code>\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            await message.answer(response_text, reply_markup=get_calculator_keyboard(), parse_mode=ParseMode.HTML)
            return

    # 7. Noma'lum buyruq yoki tushunarsiz matn
    await message.answer(
        "🤔 <b>Kiritilgan matn aniqlanmadi.</b>\n\n"
        "Quyidagilardan birini kiritib ko'ring:\n"
        "• <b>Reaksiya:</b> <code>H2 + O2 = H2O</code>\n"
        "• <b>Formula:</b> <code>H2SO4</code> yoki <code>Ca(OH)2</code>\n"
        "• <b>Element:</b> <code>Fe</code> yoki <code>Oltin</code>\n"
        "• <b>Matematik misol:</b> <code>2500 * 4 + 10%</code>\n\n"
        "Yoki /start buyrug'i orqali menyuni oching.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


# ==========================================
# ASOSIY ISHGA TUSHIRISH (ENTRYPOINT)
# ==========================================

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "XATOLIK: Bot tokeni topilmadi!\n"
            "Iltimos, Railway Variables yoki .env fayliga CALCULATOR_BOT_TOKEN ni kiriting."
        )
        return

    bot = Bot(token=BOT_TOKEN)
    logger.info("Universal Kimyo & Matematika Kalkulyatori Boti ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
