"""
Kimyo Kalkulyatori va Matematik Kalkulyator uchun Telegram Inline klaviaturalari
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Kimyo kalkulyatori asosiy menyusi
    """
    keyboard = [
        [
            InlineKeyboardButton(text="⚖️ Reaksiya tenglashtirish", callback_data="chem:menu:balance"),
            InlineKeyboardButton(text="🧪 Molyar massa (Mr)", callback_data="chem:menu:mr"),
        ],
        [
            InlineKeyboardButton(text="📊 Stexiometriya (n, m, V)", callback_data="chem:menu:stechio"),
            InlineKeyboardButton(text="💧 Eritmalar (w%)", callback_data="chem:menu:solution"),
        ],
        [
            InlineKeyboardButton(text="⚛️ Davriy sistema (Element)", callback_data="chem:menu:element"),
            InlineKeyboardButton(text="🧮 Arifmetik kalkulyator", callback_data="chem:menu:calc"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Botdan foydalanish qo'llanmasi", callback_data="chem:menu:help"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quick_balance_keyboard() -> InlineKeyboardMarkup:
    """
    Reaksiya tenglashtirish uchun tezkor namunalar
    """
    keyboard = [
        [
            InlineKeyboardButton(text="H2 + O2 = H2O", callback_data="chem:eq:H2 + O2 = H2O"),
            InlineKeyboardButton(text="Fe + Cl2 = FeCl3", callback_data="chem:eq:Fe + Cl2 = FeCl3"),
        ],
        [
            InlineKeyboardButton(text="C2H6 + O2 = CO2 + H2O", callback_data="chem:eq:C2H6 + O2 = CO2 + H2O"),
        ],
        [
            InlineKeyboardButton(text="KMnO4 + HCl = KCl + MnCl2 + Cl2 + H2O", callback_data="chem:eq:KMnO4 + HCl = KCl + MnCl2 + Cl2 + H2O"),
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="chem:menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quick_mr_keyboard() -> InlineKeyboardMarkup:
    """
    Molyar massani hisoblash uchun namunalar
    """
    keyboard = [
        [
            InlineKeyboardButton(text="H2SO4", callback_data="chem:mr:H2SO4"),
            InlineKeyboardButton(text="Ca(OH)2", callback_data="chem:mr:Ca(OH)2"),
        ],
        [
            InlineKeyboardButton(text="CuSO4*5H2O", callback_data="chem:mr:CuSO4*5H2O"),
            InlineKeyboardButton(text="C6H12O6", callback_data="chem:mr:C6H12O6"),
        ],
        [
            InlineKeyboardButton(text="K4[Fe(CN)6]", callback_data="chem:mr:K4[Fe(CN)6]"),
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="chem:menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    Orqaga qaytish tugmasi
    """
    keyboard = [
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="chem:menu:main"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_calculator_keyboard() -> InlineKeyboardMarkup:
    """
    Oddiy arifmetik kalkulyatorning to'liq interaktiv tugmalar paneli
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
        # 7-qator: Kimyo menyusiga qaytish
        [
            InlineKeyboardButton(text="🧪 Kimyo menyusiga o'tish", callback_data="chem:menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_calculator_display(expression: str = "", result: str = "", error: str = "") -> str:
    """
    Kalkulyator ekrani ko'rinishidagi chiroyli xabar matnini hosil qiladi.
    """
    expr_text = expression if expression else "0"
    
    lines = [
        "🧮 <b>Interaktiv Matematik Kalkulyator</b>",
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
