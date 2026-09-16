"""
Interaktiv kalkulyator uchun Telegram Inline klaviaturalari
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_calculator_keyboard() -> InlineKeyboardMarkup:
    """
    Kalkulyatorning to'liq interaktiv tugmalar panelini qaytaradi.
    """
    keyboard = [
        # 1-qator: Tozalash, O'chirish, Qavslar
        [
            InlineKeyboardButton(text="🧹 C", callback_data="calc:clear"),
            InlineKeyboardButton(text="⌫", callback_data="calc:back"),
            InlineKeyboardButton(text="(", callback_data="calc:btn:("),
            InlineKeyboardButton(text=")", callback_data="calc:btn:)"),
        ],
        # 2-qator: 7, 8, 9, Bo'lish
        [
            InlineKeyboardButton(text="7", callback_data="calc:btn:7"),
            InlineKeyboardButton(text="8", callback_data="calc:btn:8"),
            InlineKeyboardButton(text="9", callback_data="calc:btn:9"),
            InlineKeyboardButton(text="÷", callback_data="calc:btn:÷"),
        ],
        # 3-qator: 4, 5, 6, Ko'paytirish
        [
            InlineKeyboardButton(text="4", callback_data="calc:btn:4"),
            InlineKeyboardButton(text="5", callback_data="calc:btn:5"),
            InlineKeyboardButton(text="6", callback_data="calc:btn:6"),
            InlineKeyboardButton(text="×", callback_data="calc:btn:×"),
        ],
        # 4-qator: 1, 2, 3, Ayirish
        [
            InlineKeyboardButton(text="1", callback_data="calc:btn:1"),
            InlineKeyboardButton(text="2", callback_data="calc:btn:2"),
            InlineKeyboardButton(text="3", callback_data="calc:btn:3"),
            InlineKeyboardButton(text="−", callback_data="calc:btn:−"),
        ],
        # 5-qator: 0, Nuqta, Foiz, Qo'shish
        [
            InlineKeyboardButton(text="0", callback_data="calc:btn:0"),
            InlineKeyboardButton(text=".", callback_data="calc:btn:."),
            InlineKeyboardButton(text="%", callback_data="calc:btn:%"),
            InlineKeyboardButton(text="+", callback_data="calc:btn:+"),
        ],
        # 6-qator: Tarix va Teng (Hisoblash)
        [
            InlineKeyboardButton(text="📜 Tarix", callback_data="calc:history"),
            InlineKeyboardButton(text="🟰 Teng (=)", callback_data="calc:equals"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_calculator_display(expression: str = "", result: str = "", error: str = "") -> str:
    """
    Kalkulyator ekrani ko'rinishidagi chiroyli xabar matnini hosil qiladi.
    """
    expr_text = expression if expression else "0"
    
    lines = [
        "🧮 <b>Interaktiv Kalkulyator</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    if error:
        lines.append(f"📝 Ifoda: <code>{expr_text}</code>")
        lines.append(f"⚠️ <b>Xatolik:</b> <i>{error}</i>")
    elif result:
        lines.append(f"📝 Ifoda: <code>{expr_text}</code>")
        lines.append(f"🎯 <b>Natija:</b> <code>{result}</code>")
    else:
        lines.append(f"📟 <b>Displey:</b> <code>{expr_text}</code>")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 <i>Tugmalarni bosing yoki chatga to'g'ridan-to'g'ri ifoda yozing!</i>")

    return "\n".join(lines)
