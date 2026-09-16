"""
Kimyo Kalkulyatori uchun Avtomatlashtirilgan Testlar
"""

import unittest
from chemistry import (
    parse_formula,
    calculate_molar_mass,
    balance_equation,
    calculate_stoichiometry,
    calculate_solution_mass_fraction,
    find_element,
)


class TestChemistryEngine(unittest.TestCase):

    def test_parse_formula(self):
        # Oddiy
        self.assertEqual(parse_formula("H2O"), {"H": 2, "O": 1})
        self.assertEqual(parse_formula("H2SO4"), {"H": 2, "S": 1, "O": 4})
        # Qavslar
        self.assertEqual(parse_formula("Ca(OH)2"), {"Ca": 1, "O": 2, "H": 2})
        self.assertEqual(parse_formula("Al2(SO4)3"), {"Al": 2, "S": 3, "O": 12})
        # Kvadrat qavslar
        self.assertEqual(parse_formula("K4[Fe(CN)6]"), {"K": 4, "Fe": 1, "C": 6, "N": 6})
        # Kristallogidratlar
        self.assertEqual(parse_formula("CuSO4*5H2O"), {"Cu": 1, "S": 1, "O": 9, "H": 10})

    def test_molar_mass(self):
        # H2SO4 = 2*1.008 + 32.06 + 4*15.999 = 98.072
        ok, res = calculate_molar_mass("H2SO4")
        self.assertTrue(ok)
        self.assertAlmostEqual(res["total_mass"], 98.072, places=2)

        # Ca(OH)2 = 40.078 + 2*(15.999 + 1.008) = 74.092
        ok, res = calculate_molar_mass("Ca(OH)2")
        self.assertTrue(ok)
        self.assertAlmostEqual(res["total_mass"], 74.092, places=2)

        # Foizlar yig'indisi ~ 100%
        fractions_sum = sum(el["fraction"] for el in res["elements"])
        self.assertAlmostEqual(fractions_sum, 100.0, places=1)

    def test_balance_equation(self):
        # Oddiy reaksiya
        ok, res, r_info, p_info = balance_equation("H2 + O2 = H2O")
        self.assertTrue(ok)
        self.assertEqual(res, "2H2 + O2 = 2H2O")

        # Al va H2SO4
        ok, res, _, _ = balance_equation("Al + H2SO4 = Al2(SO4)3 + H2")
        self.assertTrue(ok)
        self.assertEqual(res, "2Al + 3H2SO4 = Al2(SO4)3 + 3H2")

        # Murakkab OVR (KMnO4 + HCl)
        ok, res, _, _ = balance_equation("KMnO4 + HCl = KCl + MnCl2 + Cl2 + H2O")
        self.assertTrue(ok)
        self.assertEqual(res, "2KMnO4 + 16HCl = 2KCl + 2MnCl2 + 5Cl2 + 8H2O")

        # Organik yonish (C2H6 + O2)
        ok, res, _, _ = balance_equation("C2H6 + O2 -> CO2 + H2O")
        self.assertTrue(ok)
        self.assertEqual(res, "2C2H6 + 7O2 = 4CO2 + 6H2O")

    def test_stoichiometry(self):
        # 36 g H2O ~ 2 mol, 44.8 L
        res = calculate_stoichiometry(formula="H2O", mass=36.0)
        self.assertAlmostEqual(res["moles"], 2.0, places=1)
        self.assertAlmostEqual(res["volume"], 44.8, places=0)

    def test_solution(self):
        # 20g tuz + 80g suv -> 100g eritma (20%)
        res = calculate_solution_mass_fraction(solute_mass=20, solvent_mass=80)
        self.assertEqual(res["fraction_percent"], 20.0)
        self.assertEqual(res["solution_mass"], 100.0)

    def test_element_search(self):
        el = find_element("Fe")
        self.assertIsNotNone(el)
        self.assertEqual(el["symbol"], "Fe")
        self.assertEqual(el["number"], 26)

        el2 = find_element("Oltin")
        self.assertIsNotNone(el2)
        self.assertEqual(el2["symbol"], "Au")


if __name__ == "__main__":
    unittest.main()
