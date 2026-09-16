"""
Xavfsiz matematik ifodalar hisoblagichi (Safe Math Evaluator)
Pythonning 'ast' (Abstract Syntax Tree) moduli orqali ishlaydi.
Xatarli kodlar (eval, exec, tizim buyruqlari) bajarilishidan 100% himoyalangan.
"""

import ast
import operator
import re
from typing import Any, Tuple, Union

# Ruxsat etilgan operatorlar ro'yxati
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class SafeMathEvaluator(ast.NodeVisitor):
    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in OPERATORS:
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Nolga bo'lish mumkin emas!")
            # Katta darajalardan xavfsizlik (masalan 999999**999999)
            if op_type is ast.Pow:
                if isinstance(right, (int, float)) and right > 1000:
                    raise ValueError("Daraja ko'rsatkichi juda katta (maksimum 1000)!")
            return OPERATORS[op_type](left, right)
        raise ValueError(f"Ruxsat etilmagan amal: {node.op}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in OPERATORS:
            return OPERATORS[op_type](operand)
        raise ValueError(f"Ruxsat etilmagan unar amal: {node.op}")

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Faqat raqamlar ruxsat etilgan: {node.value}")

    # Python < 3.8 mosligi uchun Num
    def visit_Num(self, node: ast.Num) -> Any:
        return node.n

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Expr(self, node: ast.Expr) -> Any:
        return self.visit(node.value)

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Ruxsat etilmagan ifoda elementi: {type(node).__name__}")


def format_number(val: Union[int, float]) -> str:
    """
    Raqamni chiroyli ko'rinishda formatlaydi:
    - 0.1 + 0.2 = 0.3
    - 1250000 -> 1 250 000
    - 1250000.5 -> 1 250 000.5
    """
    if isinstance(val, float):
        # Yaxlitlash xatolarini to'g'irlash (masalan 0.30000000000000004)
        val = round(val, 10)
        if val.is_integer():
            val = int(val)

    if isinstance(val, int):
        return f"{val:,}".replace(",", " ")
    
    # Float bo'lsa
    parts = f"{val:f}".rstrip("0").rstrip(".").split(".")
    integer_part = f"{int(parts[0]):,}".replace(",", " ")
    if len(parts) > 1:
        return f"{integer_part}.{parts[1]}"
    return integer_part


def normalize_expression(expr: str) -> str:
    """
    Matnli ifodani matematik standartga keltiradi:
    - '×' -> '*'
    - '÷' -> '/'
    - '−' -> '-'
    - '^' -> '**'
    - '500 + 10%' -> '500 + (500 * 0.1)'
    - '20%' -> '(20 / 100)'
    """
    cleaned = expr.strip()
    cleaned = cleaned.replace("×", "*").replace("x", "*").replace("X", "*")
    cleaned = cleaned.replace("÷", "/").replace(":", "/")
    cleaned = cleaned.replace("−", "-").replace("—", "-")
    cleaned = cleaned.replace("^", "**")

    # Foiz amallarini to'g'irlash:
    # 1) A + B% -> A + (A * (B/100))
    # 2) A - B% -> A - (A * (B/100))
    cleaned = re.sub(
        r'(\d+(?:\.\d+)?)\s*([\+\-])\s*(\d+(?:\.\d+)?)\s*%',
        r'\1 \2 (\1 * \3 / 100)',
        cleaned
    )
    # 3) Oddiy B% -> (B / 100)
    cleaned = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1 / 100)', cleaned)

    return cleaned


def calculate(expression: str) -> Tuple[bool, Union[int, float, str], str]:
    """
    Ifodani xavfsiz hisoblaydi.
    Qaytaradi: (muvaffaqiyatli: bool, natija_yoki_xato: Any, formatlangan_natija: str)
    """
    if not expression or not expression.strip():
        return False, "Ifoda bo'sh!", ""

    normalized = normalize_expression(expression)

    # Ruxsat etilmagan belgilarni tekshirish
    if re.search(r'[^0-9\+\-\*\/\%\.\(\)\s\*\*\s]', normalized):
        return False, "Ifodada noaniq belgilar mavjud!", ""

    try:
        parsed = ast.parse(normalized, mode='eval')
        evaluator = SafeMathEvaluator()
        raw_result = evaluator.visit(parsed)
        formatted = format_number(raw_result)
        return True, raw_result, formatted
    except ZeroDivisionError:
        return False, "Nolga bo'lish mumkin emas!", ""
    except (SyntaxError, ValueError) as e:
        return False, f"Xato ifoda: {str(e)}", ""
    except OverflowError:
        return False, "Natija juda katta (cheksiz)! ", ""
    except Exception as e:
        return False, f"Hisoblashda xatolik yuz berdi: {str(e)}", ""
