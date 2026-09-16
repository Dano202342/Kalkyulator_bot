"""
Kimyo Kalkulyatori Asosiy Algoritmlari Moduli (Chemistry Engine)
- 118 ta element davriy jadvali (Mendeleyev jadvali)
- Kimyoviy formulalarni tahlil qilish (qavslar, kristallogidratlar)
- Molyar massa (Mr) va elementlarning massa ulushlarini (w%) hisoblash
- Kimyoviy tenglamalarni Gauss-Jordan / Nullspace usuli bilan tenglashtirish
- Stexiometriya (mol, massa, hajm, zarrachalar soni)
- Eritmalar konsentratsiyasi hisoblari
"""

import math
import re
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, Union

# Avogadro soni va Molyar hajm (n.sh.)
AVOGADRO = 6.02214076e23
MOLAR_VOLUME = 22.414  # L/mol

# Mendeleyev davriy jadvali: (belgi: [atom_raqami, nomi_uz, atom_massasi, guruhi, davri])
PERIODIC_TABLE: Dict[str, Tuple[int, str, float, int, int]] = {
    "H": (1, "Vodorod", 1.008, 1, 1),
    "He": (2, "Geliy", 4.0026, 8, 1),
    "Li": (3, "Litiy", 6.94, 1, 2),
    "Be": (4, "Berilliy", 9.0122, 2, 2),
    "B": (5, "Bor", 10.81, 3, 2),
    "C": (6, "Uglerod", 12.011, 4, 2),
    "N": (7, "Azot", 14.007, 5, 2),
    "O": (8, "Kislorod", 15.999, 6, 2),
    "F": (9, "Ftor", 18.998, 7, 2),
    "Ne": (10, "Neon", 20.180, 8, 2),
    "Na": (11, "Natriy", 22.990, 1, 3),
    "Mg": (12, "Magniy", 24.305, 2, 3),
    "Al": (13, "Alyuminiy", 26.982, 3, 3),
    "Si": (14, "Kremniy", 28.085, 4, 3),
    "P": (15, "Fosfor", 30.974, 5, 3),
    "S": (16, "Oltingugurt", 32.06, 6, 3),
    "Cl": (17, "Xlor", 35.45, 7, 3),
    "Ar": (18, "Argon", 39.948, 8, 3),
    "K": (19, "Kaliy", 39.098, 1, 4),
    "Ca": (20, "Kalsiy", 40.078, 2, 4),
    "Sc": (21, "Skandiy", 44.956, 3, 4),
    "Ti": (22, "Titan", 47.867, 4, 4),
    "V": (23, "Vanadiy", 50.942, 5, 4),
    "Cr": (24, "Xrom", 51.996, 6, 4),
    "Mn": (25, "Marganets", 54.938, 7, 4),
    "Fe": (26, "Temir", 55.845, 8, 4),
    "Co": (27, "Kobalt", 58.933, 8, 4),
    "Ni": (28, "Nikel", 58.693, 8, 4),
    "Cu": (29, "Mis", 63.546, 1, 4),
    "Zn": (30, "Rux", 65.38, 2, 4),
    "Ga": (31, "Galliy", 69.723, 3, 4),
    "Ge": (32, "Germaniy", 72.630, 4, 4),
    "As": (33, "Mishyak", 74.922, 5, 4),
    "Se": (34, "Selen", 78.971, 6, 4),
    "Br": (35, "Brom", 79.904, 7, 4),
    "Kr": (36, "Kripton", 83.798, 8, 4),
    "Rb": (37, "Rubidiy", 85.468, 1, 5),
    "Sr": (38, "Stronsiy", 87.62, 2, 5),
    "Y": (39, "Ittriy", 88.906, 3, 5),
    "Zr": (40, "Sirkoniy", 91.224, 4, 5),
    "Nb": (41, "Niobiy", 92.906, 5, 5),
    "Mo": (42, "Molibden", 95.95, 6, 5),
    "Tc": (43, "Texnetsiy", 98.0, 7, 5),
    "Ru": (44, "Ruteniy", 101.07, 8, 5),
    "Rh": (45, "Rodiy", 102.91, 8, 5),
    "Pd": (46, "Palladiy", 106.42, 8, 5),
    "Ag": (47, "Kumush", 107.87, 1, 5),
    "Cd": (48, "Kadmiy", 112.41, 2, 5),
    "In": (49, "Indiy", 114.82, 3, 5),
    "Sn": (50, "Qalay", 118.71, 4, 5),
    "Sb": (51, "Surma", 121.76, 5, 5),
    "Te": (52, "Tellur", 127.60, 6, 5),
    "I": (53, "Yod", 126.90, 7, 5),
    "Xe": (54, "Ksenon", 131.29, 8, 5),
    "Cs": (55, "Seziy", 132.91, 1, 6),
    "Ba": (56, "Bariy", 137.33, 2, 6),
    "La": (57, "Lantan", 138.91, 3, 6),
    "Ce": (58, "Seriy", 140.12, 3, 6),
    "Pr": (59, "Prazeodim", 140.91, 3, 6),
    "Nd": (60, "Neodim", 144.24, 3, 6),
    "Pm": (61, "Prometiy", 145.0, 3, 6),
    "Sm": (62, "Samariy", 150.36, 3, 6),
    "Eu": (63, "Yevropiy", 151.96, 3, 6),
    "Gd": (64, "Gadoliniy", 157.25, 3, 6),
    "Tb": (65, "Terbiy", 158.93, 3, 6),
    "Dy": (66, "Disproziy", 162.50, 3, 6),
    "Ho": (67, "Golmiy", 164.93, 3, 6),
    "Er": (68, "Erbiy", 167.26, 3, 6),
    "Tm": (69, "Tuliy", 168.93, 3, 6),
    "Yb": (70, "Itterbiy", 173.05, 3, 6),
    "Lu": (71, "Lyutetsiy", 174.97, 3, 6),
    "Hf": (72, "Gafniy", 178.49, 4, 6),
    "Ta": (73, "Tantal", 180.95, 5, 6),
    "W": (74, "Volfram", 183.84, 6, 6),
    "Re": (75, "Reniy", 186.21, 7, 6),
    "Os": (76, "Osmiy", 190.23, 8, 6),
    "Ir": (77, "Iridiy", 192.22, 8, 6),
    "Pt": (78, "Platina", 195.08, 8, 6),
    "Au": (79, "Oltin", 196.97, 1, 6),
    "Hg": (80, "Simob", 200.59, 2, 6),
    "Tl": (81, "Talliy", 204.38, 3, 6),
    "Pb": (82, "Qo'rg'oshin", 207.2, 4, 6),
    "Bi": (83, "Vismut", 208.98, 5, 6),
    "Po": (84, "Poloniy", 209.0, 6, 6),
    "At": (85, "Astat", 210.0, 7, 6),
    "Rn": (86, "Radon", 222.0, 8, 6),
    "Fr": (87, "Fransiy", 223.0, 1, 7),
    "Ra": (88, "Radiy", 226.0, 2, 7),
    "Ac": (89, "Aktiniy", 227.0, 3, 7),
    "Th": (90, "Toriy", 232.04, 3, 7),
    "Pa": (91, "Protaktiniy", 231.04, 3, 7),
    "U": (92, "Uran", 238.03, 3, 7),
    "Np": (93, "Neptuniy", 237.0, 3, 7),
    "Pu": (94, "Plutoniy", 244.0, 3, 7),
    "Am": (95, "Ameritsiy", 243.0, 3, 7),
    "Cm": (96, "Kyuriy", 247.0, 3, 7),
    "Bk": (97, "Berkliy", 247.0, 3, 7),
    "Cf": (98, "Kaliforniy", 251.0, 3, 7),
    "Es": (99, "Eynshteyniy", 252.0, 3, 7),
    "Fm": (100, "Fermiy", 257.0, 3, 7),
    "Md": (101, "Mendeleyeviy", 258.0, 3, 7),
    "No": (102, "Nobeliy", 259.0, 3, 7),
    "Lr": (103, "Lourensiy", 262.0, 3, 7),
    "Rf": (104, "Rezerfordiy", 267.0, 4, 7),
    "Db": (105, "Dubniy", 270.0, 5, 7),
    "Sg": (106, "Siborgiy", 271.0, 6, 7),
    "Bh": (107, "Boriy", 270.0, 7, 7),
    "Hs": (108, "Xassiy", 277.0, 8, 7),
    "Mt": (109, "Meytneriy", 276.0, 8, 7),
    "Ds": (110, "Darmshtadtiy", 281.0, 8, 7),
    "Rg": (111, "Rentgeniy", 280.0, 1, 7),
    "Cn": (112, "Kopernitsiy", 285.0, 2, 7),
    "Nh": (113, "Nixoniy", 284.0, 3, 7),
    "Fl": (114, "Fleroviy", 289.0, 4, 7),
    "Mc": (115, "Moskoviy", 288.0, 5, 7),
    "Lv": (116, "Livermoriy", 293.0, 6, 7),
    "Ts": (117, "Tennessin", 294.0, 7, 7),
    "Og": (118, "Oganeson", 294.0, 8, 7),
}


def parse_formula(formula: str) -> Dict[str, int]:
    """
    Kimyoviy formulani tahlil qilib, har bir element sonini lug'at ko'rinishida qaytaradi.
    Qo'llab-quvvatlaydi:
    - Oddiy formulalar: H2O, H2SO4, NaCl
    - Qavslar: Ca(OH)2, Al2(SO4)3, [Cu(NH3)4]SO4, K4[Fe(CN)6]
    - Kristallogidratlar: CuSO4*5H2O, FeSO4.7H2O, Na2CO3·10H2O
    - Oldidagi koeffitsiyentlar: 2H2O -> H:4, O:2
    """
    cleaned = formula.strip().replace(" ", "")
    if not cleaned:
        return {}

    # Kristallogidratlarni bo'lish (*, ·, .)
    parts = re.split(r"[\*·]", cleaned)
    if len(parts) == 1 and "." in cleaned:
        dot_split = re.split(r"(?<=[A-Za-z\)\]])\.", cleaned)
        if len(dot_split) > 1:
            parts = dot_split

    if len(parts) > 1:
        total_counts: Dict[str, int] = {}
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = re.match(r"^(\d+)(.*)$", part)
            if m:
                coef = int(m.group(1))
                sub_formula = m.group(2)
            else:
                coef = 1
                sub_formula = part

            sub_counts = _parse_single_formula(sub_formula)
            for elem, cnt in sub_counts.items():
                total_counts[elem] = total_counts.get(elem, 0) + cnt * coef
        return total_counts

    return _parse_single_formula(cleaned)


def _parse_single_formula(formula: str) -> Dict[str, int]:
    """
    Bitta formulani (kristall qismi bo'lmagan) tahlil qiladi.
    Kvadrat va oddiy qavslarni qamrab oladi.
    """
    leading_match = re.match(r"^(\d+)(.*)$", formula)
    if leading_match:
        leading_coef = int(leading_match.group(1))
        formula = leading_match.group(2)
    else:
        leading_coef = 1

    formula = formula.replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")")

    def parse_tokens(tokens: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i] == "(":
                open_brackets = 1
                j = i + 1
                while j < n and open_brackets > 0:
                    if tokens[j] == "(":
                        open_brackets += 1
                    elif tokens[j] == ")":
                        open_brackets -= 1
                    j += 1
                
                if open_brackets > 0:
                    raise ValueError("Qavslar to'g'ri yopilmagan!")

                inside_tokens = tokens[i + 1 : j - 1]
                sub_match = re.match(r"^\d+", tokens[j:])
                if sub_match:
                    sub_multiplier = int(sub_match.group(0))
                    i = j + len(sub_match.group(0))
                else:
                    sub_multiplier = 1
                    i = j

                sub_counts = parse_tokens(inside_tokens)
                for el, count in sub_counts.items():
                    counts[el] = counts.get(el, 0) + count * sub_multiplier

            else:
                elem_match = re.match(r"^([A-Z][a-z]?)(\d*)", tokens[i:])
                if elem_match:
                    elem = elem_match.group(1)
                    num_str = elem_match.group(2)
                    count = int(num_str) if num_str else 1
                    if elem not in PERIODIC_TABLE:
                        raise ValueError(f"Noma'lum kimyoviy element belgisi: '{elem}'")
                    counts[elem] = counts.get(elem, 0) + count
                    i += len(elem_match.group(0))
                else:
                    raise ValueError(f"Formulada xatolik (belgi: '{tokens[i]}')")

        return counts

    raw_counts = parse_tokens(formula)
    if leading_coef != 1:
        return {k: v * leading_coef for k, v in raw_counts.items()}
    return raw_counts


def calculate_molar_mass(formula: str) -> Tuple[bool, Union[Dict, str]]:
    """
    Formulaning molyar massasi (Mr) va elementlarning massa ulushlarini hisoblaydi.
    """
    try:
        counts = parse_formula(formula)
        if not counts:
            return False, "Formula bo'sh yoki noto'g'ri kiritilgan."

        total_mass = 0.0
        details = []

        for symbol, count in counts.items():
            atomic_number, uz_name, atomic_mass, group, period = PERIODIC_TABLE[symbol]
            elem_total = count * atomic_mass
            total_mass += elem_total
            details.append({
                "symbol": symbol,
                "name": uz_name,
                "count": count,
                "atomic_mass": atomic_mass,
                "total_mass": elem_total,
                "number": atomic_number,
                "group": group,
                "period": period,
            })

        for item in details:
            item["fraction"] = round((item["total_mass"] / total_mass) * 100, 3)

        return True, {
            "formula": formula.strip(),
            "total_mass": round(total_mass, 4),
            "elements": details,
        }
    except Exception as e:
        return False, str(e)


def balance_equation(equation_str: str) -> Tuple[bool, str, List[Tuple[str, int]], List[Tuple[str, int]]]:
    """
    Kimyoviy tenglamani tenglashtirish.
    Kiritish: "H2 + O2 = H2O" yoki "KMnO4 + HCl -> KCl + MnCl2 + Cl2 + H2O"
    Qaytaradi: (Muvaffaqiyatli, Tenglashtirilgan_tenglama, Reagentlar_ro'yxati, Mahsulotlar_ro'yxati)
    """
    try:
        eq_clean = equation_str.replace("=>", "=").replace("->", "=").replace("⇌", "=").replace("⇄", "=")
        if "=" not in eq_clean:
            return False, "Tenglamada '=' yoki '->' belgisi bo'lishi kerak!", [], []

        left_side, right_side = eq_clean.split("=", 1)
        reactants = [r.strip() for r in left_side.split("+") if r.strip()]
        products = [p.strip() for p in right_side.split("+") if p.strip()]

        if not reactants or not products:
            return False, "Reagentlar yoki mahsulotlar topilmadi!", [], []

        def clean_molecule(mol: str) -> str:
            return re.sub(r"^\s*\d+\s*", "", mol).strip()

        clean_reactants = [clean_molecule(r) for r in reactants]
        clean_products = [clean_molecule(p) for p in products]
        all_molecules = clean_reactants + clean_products

        all_elements = set()
        mol_element_maps = []
        for mol in all_molecules:
            parsed = parse_formula(mol)
            if not parsed:
                return False, f"Molekula tahlil qilinmadi: {mol}", [], []
            mol_element_maps.append(parsed)
            all_elements.update(parsed.keys())

        element_list = sorted(list(all_elements))
        num_compounds = len(all_molecules)

        matrix: List[List[Fraction]] = []
        for elem in element_list:
            row = []
            for i, mol_map in enumerate(mol_element_maps):
                cnt = mol_map.get(elem, 0)
                if i < len(clean_reactants):
                    row.append(Fraction(cnt, 1))
                else:
                    row.append(Fraction(-cnt, 1))
            matrix.append(row)

        solution_vector = _find_nullspace_integer_vector(matrix, num_compounds)
        if not solution_vector:
            return False, "Ushbu kimyoviy tenglamani tenglashtirib bo'lmadi (reaksiya xato yoki elementlar mutanosib emas)!", [], []

        react_coefs = solution_vector[: len(clean_reactants)]
        prod_coefs = solution_vector[len(clean_reactants) :]

        def format_side(molecules: List[str], coefs: List[int]) -> Tuple[str, List[Tuple[str, int]]]:
            parts = []
            info_list = []
            for mol, c in zip(molecules, coefs):
                info_list.append((mol, c))
                if c == 1:
                    parts.append(mol)
                else:
                    parts.append(f"{c}{mol}")
            return " + ".join(parts), info_list

        left_formatted, react_info = format_side(clean_reactants, react_coefs)
        right_formatted, prod_info = format_side(clean_products, prod_coefs)
        balanced_eq = f"{left_formatted} = {right_formatted}"

        return True, balanced_eq, react_info, prod_info

    except Exception as e:
        return False, f"Xatolik: {str(e)}", [], []


def _find_nullspace_integer_vector(matrix: List[List[Fraction]], num_vars: int) -> Optional[List[int]]:
    """
    A * x = 0 tenglamalar tizimi uchun eng kichik musbat butun sonlardan iborat yechim vektorini topadi.
    """
    rows = len(matrix)
    cols = num_vars

    mat = [[val for val in row] for row in matrix]

    lead = 0
    pivot_cols = []
    for r in range(rows):
        if lead >= cols:
            break
        i = r
        while i < rows and mat[i][lead] == 0:
            i += 1
        if i == rows:
            lead += 1
            continue
        mat[i], mat[r] = mat[r], mat[i]
        pivot_val = mat[r][lead]
        mat[r] = [val / pivot_val for val in mat[r]]
        for k in range(rows):
            if k != r and mat[k][lead] != 0:
                factor = mat[k][lead]
                mat[k] = [mat[k][c] - factor * mat[r][c] for c in range(cols)]
        pivot_cols.append(lead)
        lead += 1

    free_cols = [c for c in range(cols) if c not in pivot_cols]
    if not free_cols:
        return None

    import itertools
    # Kichik musbat butun qiymatlar kombinatsiyasini sinash (1..15)
    for max_bound in [1, 2, 4, 8, 15]:
        for combo in itertools.product(range(1, max_bound + 1), repeat=len(free_cols)):
            sol = [Fraction(0, 1)] * cols
            for fc, c_val in zip(free_cols, combo):
                sol[fc] = Fraction(c_val, 1)

            valid = True
            for r_idx, p_col in enumerate(pivot_cols):
                val = -sum(mat[r_idx][fc] * sol[fc] for fc in free_cols)
                if val <= 0:
                    valid = False
                    break
                sol[p_col] = val

            if valid and all(val > 0 for val in sol):
                denominators = [val.denominator for val in sol]
                lcm_val = 1
                for d in denominators:
                    lcm_val = (lcm_val * d) // math.gcd(lcm_val, d)

                int_solution = [int(val * lcm_val) for val in sol]
                gcd_all = int_solution[0]
                for num in int_solution[1:]:
                    gcd_all = math.gcd(gcd_all, num)
                return [x // gcd_all for x in int_solution]

    return None


def calculate_stoichiometry(
    formula: Optional[str] = None,
    mass: Optional[float] = None,
    moles: Optional[float] = None,
    volume: Optional[float] = None,
    particles: Optional[float] = None,
) -> Dict[str, Union[float, str]]:
    """
    Stexiometrik hisob-kitoblar: n, m, V, N bog'liqliklari.
    """
    molar_mass = None
    if formula:
        success, res = calculate_molar_mass(formula)
        if success:
            molar_mass = res["total_mass"]

    n = None
    if moles is not None and moles > 0:
        n = moles
    elif mass is not None and mass > 0 and molar_mass:
        n = mass / molar_mass
    elif volume is not None and volume > 0:
        n = volume / MOLAR_VOLUME
    elif particles is not None and particles > 0:
        n = particles / AVOGADRO

    if n is None:
        raise ValueError("Hisoblash uchun yetarli ma'lumot berilmagan yoki qiymatlar noto'g'ri!")

    calc_moles = n
    calc_volume = n * MOLAR_VOLUME
    calc_particles = n * AVOGADRO
    calc_mass = (n * molar_mass) if molar_mass else None

    return {
        "formula": formula or "Noma'lum modda",
        "molar_mass": round(molar_mass, 4) if molar_mass else None,
        "moles": round(calc_moles, 6),
        "mass": round(calc_mass, 4) if calc_mass is not None else None,
        "volume": round(calc_volume, 4),
        "particles": f"{calc_particles:.4e}",
    }


def calculate_solution_mass_fraction(
    solute_mass: Optional[float] = None,
    solution_mass: Optional[float] = None,
    solvent_mass: Optional[float] = None,
    fraction_percent: Optional[float] = None,
) -> Dict[str, float]:
    """
    Eritmaning massa ulushini hisoblash (w% = m_erigan / m_eritma * 100).
    """
    if solute_mass is not None and solution_mass is not None:
        if solution_mass <= 0 or solute_mass < 0 or solute_mass > solution_mass:
            raise ValueError("Modda massasi eritma massasidan katta bo'lishi mumkin emas!")
        w = (solute_mass / solution_mass) * 100
        solvent = solution_mass - solute_mass
        return {
            "solute_mass": round(solute_mass, 4),
            "solution_mass": round(solution_mass, 4),
            "solvent_mass": round(solvent, 4),
            "fraction_percent": round(w, 4),
        }

    if solute_mass is not None and solvent_mass is not None:
        sol_mass = solute_mass + solvent_mass
        w = (solute_mass / sol_mass) * 100
        return {
            "solute_mass": round(solute_mass, 4),
            "solution_mass": round(sol_mass, 4),
            "solvent_mass": round(solvent_mass, 4),
            "fraction_percent": round(w, 4),
        }

    if solution_mass is not None and fraction_percent is not None:
        solute = (fraction_percent / 100) * solution_mass
        solvent = solution_mass - solute
        return {
            "solute_mass": round(solute, 4),
            "solution_mass": round(solution_mass, 4),
            "solvent_mass": round(solvent, 4),
            "fraction_percent": round(fraction_percent, 4),
        }

    if solute_mass is not None and fraction_percent is not None and fraction_percent > 0:
        sol_mass = (solute_mass * 100) / fraction_percent
        solvent = sol_mass - solute_mass
        return {
            "solute_mass": round(solute_mass, 4),
            "solution_mass": round(sol_mass, 4),
            "solvent_mass": round(solvent, 4),
            "fraction_percent": round(fraction_percent, 4),
        }

    raise ValueError("Hisoblash uchun kamida 2 ta parametr kerak!")


def find_element(query: str) -> Optional[Dict[str, Union[str, int, float]]]:
    """
    Elementni belgisi, nomi yoki tartib raqami bo'yicha qidiradi.
    """
    q = query.strip()
    if q.capitalize() in PERIODIC_TABLE:
        symbol = q.capitalize()
        num, name, mass, gr, per = PERIODIC_TABLE[symbol]
        return {
            "symbol": symbol,
            "number": num,
            "name": name,
            "mass": mass,
            "group": gr,
            "period": per,
        }

    if q.isdigit():
        target_num = int(q)
        for sym, (num, name, mass, gr, per) in PERIODIC_TABLE.items():
            if num == target_num:
                return {
                    "symbol": sym,
                    "number": num,
                    "name": name,
                    "mass": mass,
                    "group": gr,
                    "period": per,
                }

    # 3. O'zbekcha yoki lotincha nomi bo'yicha to'liq moslik
    q_lower = q.lower()
    for sym, (num, name, mass, gr, per) in PERIODIC_TABLE.items():
        if q_lower == name.lower():
            return {
                "symbol": sym,
                "number": num,
                "name": name,
                "mass": mass,
                "group": gr,
                "period": per,
            }

    # 4. Qisman moslik (substring)
    for sym, (num, name, mass, gr, per) in PERIODIC_TABLE.items():
        if q_lower in name.lower():
            return {
                "symbol": sym,
                "number": num,
                "name": name,
                "mass": mass,
                "group": gr,
                "period": per,
            }

    return None

