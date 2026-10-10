"""Tests fuer stammbruch_loglog.py  (python3 -m unittest -v)"""

import math
import random
import unittest
from fractions import Fraction

import stammbruch_loglog as sb


def summe(nenner):
    return sum(Fraction(1, n) for n in nenner)


class TestHilfsfunktionen(unittest.TestCase):
    def test_primzahlen(self):
        self.assertEqual(sb.primzahlen_ab(1, 5), [3, 5, 7, 11, 13])
        self.assertTrue(sb.ist_primzahl(2**61 - 1))
        self.assertFalse(sb.ist_primzahl(3215031751))  # starke Pseudoprimzahl zu 2,3,5,7

    def test_greedy_vorlauf_lemma_2_3(self):
        rng = random.Random(1)
        for _ in range(200):
            b = rng.randrange(3, 10**12)
            a = rng.randrange(1, b)
            T = b**3
            terme, A, C = sb.greedy_vorlauf(a, b, T)
            self.assertEqual(summe(terme) + Fraction(A, C), Fraction(a, b))
            self.assertLessEqual(A, a)
            schranke = 1 + math.ceil(math.log2(math.log(T) / math.log(2)))
            self.assertLessEqual(len(terme), schranke)
            if A:
                self.assertTrue(T <= C < T * T)

    def test_takenouchi_lemma_2_2(self):
        rng = random.Random(2)
        for _ in range(300):
            liste = [rng.randrange(3, 40) for _ in range(rng.randrange(1, 8))]
            if summe(liste) >= 1:
                continue
            neu = sb.verschiedene_nenner(liste)
            self.assertEqual(len(neu), len(liste))
            self.assertEqual(len(set(neu)), len(neu))
            self.assertEqual(summe(neu), summe(liste))
            self.assertTrue(all(n >= 2 for n in neu))

    def test_teilerlisten_teilen_M(self):
        H = sb.Hilfsnenner.konstruiere(40.0, sb.Parameter(R=2))
        rng = random.Random(3)
        for li in range(len(H.listen)):
            for _ in range(50):
                t = H.eintrag(li, rng.randrange(2**H.m))
                self.assertEqual(H.M % t, 0)
        self.assertEqual(H.M % (1 << H.a), 0)

    def test_residuen(self):
        H = sb.Hilfsnenner.konstruiere(30.0, sb.Parameter(m_max=8))
        u, Q = 987654321987, 12345678901234567
        for li in range(len(H.listen)):
            res = H.residuen(li, u, Q)
            for i in (0, 1, 77, len(res) - 1):
                self.assertEqual(res[i], (-Q * H.eintrag(li, i)) % u)

    def test_residuen_identitaet(self):
        H = sb.Hilfsnenner.konstruiere(30.0, sb.Parameter(m_max=8))
        A = sb.Abstieg(H, sb.Parameter(m_max=8), e_S=10**13)
        u, Q = 10**20 + 7, 10**25 + 3
        h0, li, idx = A.kandidaten(u, Q)[0]
        d, z, h = A.schritt(u, Q, li, idx)
        self.assertEqual(h, h0)
        self.assertEqual(Fraction(u, H.M * Q), Fraction(1, d) + Fraction(h, H.M * Q * z))


class TestZerlegung(unittest.TestCase):
    def pruefe(self, a, b, par=None):
        e = sb.stammbruchzerlegung(a, b, par)
        self.assertTrue(e.pruefe(), (a, b))
        self.assertEqual(summe(e.nenner), Fraction(a, b))
        return e

    def test_kleine_brueche_vollstaendig(self):
        for b in range(2, 40):
            for a in range(1, b):
                self.pruefe(a, b)

    def test_zufaellige_brueche(self):
        rng = random.Random(4)
        for stellen in (8, 15, 30):
            for _ in range(4):
                b = rng.randrange(10 ** (stellen - 1), 10**stellen)
                self.pruefe(rng.randrange(1, b), b)

    def test_b_minus_1(self):
        for b in (10**6 + 3, 2**40, 10**25 + 1):
            self.pruefe(b - 1, b)

    def test_paper_modus(self):
        par = sb.Parameter(R=2, m_max=10)
        rng = random.Random(5)
        b = rng.randrange(10**19, 10**20)
        self.pruefe(rng.randrange(1, b), b, par)

    def test_untere_schranke(self):
        # Beweis von Satz 1.1: jede Zerlegung von (b-1)/b hat k Terme mit
        # log log b <= (1 + log 2) k + kleiner Rest; insbesondere b <= (k+1)^(2^k).
        b = 10**30 + 57
        e = self.pruefe(b - 1, b)
        k = e.laenge
        self.assertLessEqual(math.log(math.log(b)), k * math.log(2) + math.log(math.log(k + 1)))


if __name__ == "__main__":
    unittest.main()
