"""
Asosiy Telegram Kalkulyator Boti (Aiogram 3)
Interaktiv tugmalar, xavfsiz ifoda hisoblagichi va xotira tarixi.
"""

import asyncio
import logging
import os
import sys
from collections import defaultdict
from typing import Dict, List

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

# calculator_bot papkasi va tashqi papkani pathga qo'shish
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculator import calculate
from keyboards import format_calculator_display, get_calculator_keyboard

# .env yuklash
load_dotenv()
BOT_TOKEN = os.getenv("CALCULATOR_BOT_TOKEN") or os.getenv("BOT_TOKEN")

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("calculator_bot")

# Foydalanuvchilar sessiyasi va tarixi (In-memory)
user_sessions: Dict[int, Dict] = defaultdict(lambda: {
    "expression": "",
    "result": "",
    "just_calculated": False
})
user_history: Dict[int, List[str]] = defaultdict(list)


def add_to_history(user_id: int, item: str) -> None:
    """Tarixga yangi yozuv qo'shish (maksimum 10 ta)"""
    history = user_history[user_id]
    history.append(item)
    if len(history) > 10:
        history.pop(0)


dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """
    /start buyrug'i - bot haqida ma'lumot va interaktiv kalkulyatorni ochadi
    """
    user_id = message.from_user.id
    user_sessions[user_id] = {
        "expression": "",
        "result": "",
        "just_calculated": False
    }

    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        "Men <b>Interaktiv Kalkulyator</b> botiman 🧮\n"
        "Quyidagi tugmalar orqali bevosita hisoblashingiz yoki chatga "
        "istalgan matematik ifodani yozib yuborishingiz mumkin.\n\n"
        "<i>Masalan: 15000 * 4 yoki 500 + 10%</i>"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)

    display = format_calculator_display(expression="", result="")
    await message.answer(
        display,
        reply_markup=get_calculator_keyboard(),
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("calc"))
async def cmd_calc(message: Message):
    """
    /calc buyrug'i - yangi kalkulyator klaviaturasini chiqaradi
    """
    user_id = message.from_user.id
    user_sessions[user_id] = {
        "expression": "",
        "result": "",
        "just_calculated": False
    }
    display = format_calculator_display(expression="", result="")
    await message.answer(
        display,
        reply_markup=get_calculator_keyboard(),
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """
    /help buyrug'i - yordam va yo'riqnoma
    """
    help_text = (
        "📖 <b>Kalkulyator Boti bo'yicha qo'llanma:</b>\n\n"
        "1. <b>Tugmalar orqali hisoblash:</b>\n"
        "   Ekrandagi 0-9, amallar va 🟰 tugmasini bosib hisoblaysiz.\n\n"
        "2. <b>Chat orqali hisoblash:</b>\n"
        "   Chatga to'g'ridan-to'g'ri ifoda yozishingiz mumkin:\n"
        "   • <code>120 * 45000</code>\n"
        "   • <code>(500000 - 150000) / 4</code>\n"
        "   • <code>1000 + 15%</code>\n"
        "   • <code>2 ^ 8</code>\n\n"
        "3. <b>Buyruqlar:</b>\n"
        "   • /calc - Yangi kalkulyatorni ochish\n"
        "   • /history - Hisob-kitoblar tarixini ko'rish\n"
        "   • /clear - Tarixni tozalash\n"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@dp.message(Command("history"))
async def cmd_history(message: Message):
    """
    /history buyrug'i - hisoblashlar tarixini ko'rsatadi
    """
    user_id = message.from_user.id
    history = user_history.get(user_id, [])

    if not history:
        await message.answer("ℹ️ Sizda hali hisob-kitoblar tarixi mavjud emas.")
        return

    lines = ["📜 <b>Oxirgi hisob-kitoblaringiz:</b>\n"]
    for i, item in enumerate(reversed(history), 1):
        lines.append(f"{i}. <code>{item}</code>")

    lines.append("\n<i>Tarixni o'chirish uchun: /clear</i>")
    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)


@dp.message(Command("clear"))
async def cmd_clear(message: Message):
    """
    /clear buyrug'i - tarixni tozalaydi
    """
    user_id = message.from_user.id
    user_history[user_id] = []
    await message.answer("🧹 Hisob-kitoblar tarixi tozalandi!")


# --- CALLBACK QUERY HANDLERS (Interaktiv tugmalar) ---

@dp.callback_query(F.data.startswith("calc:"))
async def handle_calculator_callback(callback: CallbackQuery):
    """
    Kalkulyatorning barcha inline tugmalarini qabul qiladi va xabarni yangilaydi
    """
    user_id = callback.from_user.id
    action = callback.data.split(":", 1)[1]
    session = user_sessions[user_id]

    current_expr = session["expression"]
    just_calc = session["just_calculated"]

    # 1. Tozalash (Clear)
    if action == "clear":
        session["expression"] = ""
        session["result"] = ""
        session["just_calculated"] = False
        text = format_calculator_display("", "")
        try:
            await callback.message.edit_text(
                text,
                reply_markup=get_calculator_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest:
            pass
        await callback.answer("Tozalandi")
        return

    # 2. Bitta o'chirish (Backspace)
    if action == "back":
        if just_calc:
            session["expression"] = ""
            session["result"] = ""
            session["just_calculated"] = False
        elif current_expr:
            session["expression"] = current_expr[:-1]

        text = format_calculator_display(session["expression"], session.get("result", ""))
        try:
            await callback.message.edit_text(
                text,
                reply_markup=get_calculator_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest:
            pass
        await callback.answer()
        return

    # 3. Tarix tugmasi
    if action == "history":
        history = user_history.get(user_id, [])
        if not history:
            await callback.answer("Hozircha tarix bo'sh!", show_alert=True)
        else:
            recent = "\n".join([f"• {h}" for h in history[-5:]])
            await callback.answer(f"Oxirgi hisoblar:\n{recent}", show_alert=True)
        return

    # 4. Tenglik / Hisoblash (Equals)
    if action == "equals":
        if not current_expr:
            await callback.answer("Avval ifodani kiriting!", show_alert=False)
            return

        success, raw_result, formatted = calculate(current_expr)
        if success:
            history_item = f"{current_expr} = {formatted}"
            add_to_history(user_id, history_item)

            session["result"] = formatted
            session["just_calculated"] = True

            text = format_calculator_display(current_expr, result=formatted)
            try:
                await callback.message.edit_text(
                    text,
                    reply_markup=get_calculator_keyboard(),
                    parse_mode=ParseMode.HTML
                )
            except TelegramBadRequest:
                pass
            await callback.answer(f"Natija: {formatted}")
        else:
            await callback.answer(str(raw_result), show_alert=True)
            text = format_calculator_display(current_expr, error=str(raw_result))
            try:
                await callback.message.edit_text(
                    text,
                    reply_markup=get_calculator_keyboard(),
                    parse_mode=ParseMode.HTML
                )
            except TelegramBadRequest:
                pass
        return

    # 5. Belgilar va raqamlar tugmasi (btn:...)
    if action.startswith("btn:"):
        char = action.split(":", 1)[1]
        operators = ["+", "−", "×", "÷", "%"]

        # Agar hozirgina hisoblangan bo'lsa:
        if just_calc:
            if char in operators:
                # Natija ustida davom ettirish (masalan: 60000 + ...)
                res_clean = session["result"].replace(" ", "")
                current_expr = res_clean + f" {char} "
            else:
                # Yangi ifoda boshlash
                current_expr = char
            session["just_calculated"] = False
            session["result"] = ""
        else:
            if char in operators:
                current_expr += f" {char} "
            else:
                current_expr += char

        session["expression"] = current_expr

        text = format_calculator_display(current_expr)
        try:
            await callback.message.edit_text(
                text,
                reply_markup=get_calculator_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest:
            pass
        await callback.answer()
        return


# --- TEXT MESSAGE HANDLER (Chatga yozilgan ifodalar) ---

@dp.message(F.text)
async def handle_text_expression(message: Message):
    """
    Chatga to'g'ridan-to'g'ri yozilgan matematik ifodalarni taniy va hisoblaydi
    """
    text = message.text.strip()
    user_id = message.from_user.id

    # Matematik belgilar yoki raqamlar borligini tekshirish
    has_digits = any(char.isdigit() for char in text)
    if not has_digits:
        await message.answer(
            "Iltimos, hisoblash uchun matematik ifoda yozing yoki /calc buyrug'ini bosing.",
            parse_mode=ParseMode.HTML
        )
        return

    success, raw_result, formatted = calculate(text)
    if success:
        history_item = f"{text} = {formatted}"
        add_to_history(user_id, history_item)

        response_text = (
            "🔢 <b>Hisoblash natijasi:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 Ifoda: <code>{text}</code>\n"
            f"🎯 <b>Natija:</b> <code>{formatted}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(
            response_text,
            reply_markup=get_calculator_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(
            f"⚠️ <b>Xatolik:</b> {raw_result}\n\n"
            "To'g'ri ifoda kiriting, masalan: <code>25000 * 4 + 10%</code>",
            parse_mode=ParseMode.HTML
        )


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "XATOLIK: Bot tokeni topilmadi!\n"
            "Iltimos, calculator_bot/.env fayliga CALCULATOR_BOT_TOKEN ni kiriting."
        )
        return

    bot = Bot(token=BOT_TOKEN)
    logger.info("Interaktiv Kalkulyator Boti ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
