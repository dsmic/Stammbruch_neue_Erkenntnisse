#!/usr/bin/env python3
"""
Stammbruchzerlegung mit O(log log b) Termen
===========================================

Konstruktive Umsetzung des Beweises aus

    OpenAI, "Short Egyptian fractions", OpenAI Math Release Preprint,
    25. September 2026 (github.com/openai/math,
    preprints/Short-Egyptian-fractions-September-25-2026).

Satz 1.1 dort: Es gibt absolute Konstanten c1, c2 > 0, so dass fuer alle
grossen b gilt

    c1 * log log b  <=  N(b)  <=  c2 * log log b,

wobei N(b) = max_{1<=a<b} N(a, b) und N(a, b) die minimale Anzahl
verschiedener Stammbrueche 1/n_1 + ... + 1/n_k = a/b ist
(Erdős-Problem #304, Vermutung von Erdős 1950).

Der Beweis ist konstruktiv. Das Programm folgt seinen Stufen
(S = log b):

  1. Greedy-Vorlauf (Lemma 2.3): O(log S) Greedy-Schritte, bis der Rest
     die Form A/C mit A <= a und grossem Nenner C hat.
  2. Hilfsnenner M (Abschnitt 4): M = 2^a * prod p_j * prod p_{i,j,0} p_{i,j,1}
     mit m ~ S/log S Primzahlen der Groesse ~ S^K. Die Teilerlisten
       T_0 = (prod_{j in I} p_j)_I            (deterministisch, "hohe" Stufen)
       T_i = (prod_j p_{i,j,I_j})_I, i=1..R   (zufaellig, "mittlere/terminale" Stufen)
     haben je 2^m Eintraege, alle Teiler von M.
  3. Residuen-Abstieg (Abschnitt 5): Fuer einen Teiler t | M gilt mit
         z = ceil(Q t / u),   h = u z - Q t   (0 <= h < u)
     die Identitaet
         u/(M Q) = 1/((M/t) z) + (1/z) * h/(M Q).
     Ein Stammbruch reduziert also den Zaehler u auf das Residuum
     h = (-Q t) mod u. Da 2^m Teiler zur Wahl stehen, ist das kleinste
     Residuum typischerweise ~ u / 2^m, d.h. jeder Schritt spart ~m Bit.
     Mit log M ~ K m log S genuegen O(log S) Schritte.
     Sobald u < M ist, wird Q = C durch Q = 1 ersetzt (Nenner * C).
  4. Binaerer Abschluss: fuer u <= 2^a ist u/M = sum 2^k/M = sum 1/(M/2^k).
  5. Dichte Menge -> jeder Zaehler (Beweis von Satz 1.1 in Abschnitt 2):
     A/C = n/(MC) mit n = g A M; ist n selbst "schlecht", wird n = u + (n-u)
     mit zwei "guten" Zaehlern zerlegt und anschliessend durch g geteilt.
  6. Doppelte Nenner entfernen (Lemma 2.2, Takenouchi):
         2/(2p)   = 1/(p+1) + 1/(p(p+1)),
         2/(2p+1) = 1/(p+1) + 1/((p+1)(2p+1)).

WICHTIG: Die Konstanten des Papers (K=100, R=1000, D0=10^5, eta=10^-4,
D_M ~ 2*10^5) sind nur fuer astronomisch grosse b sinnvoll. Das Programm
verwendet dieselbe Konstruktion mit praktikablen, einstellbaren
Parametern. Das Ergebnis wird immer exakt (mit Bruchrechnung) geprueft;
die Laenge ist dann empirisch mit log log b zu vergleichen.
"""

from __future__ import annotations

import argparse
import heapq
import math
import random
import sys
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Zahlentheoretische Hilfsfunktionen
# ---------------------------------------------------------------------------

_KLEINE_PRIMZAHLEN = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


def ist_primzahl(n: int) -> bool:
    """Miller-Rabin; deterministisch fuer n < 3.3 * 10^24."""
    if n < 2:
        return False
    for p in _KLEINE_PRIMZAHLEN:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def primzahlen_ab(start: int, anzahl: int) -> List[int]:
    """Die ersten `anzahl` ungeraden Primzahlen >= start."""
    p = max(3, start) | 1
    erg: List[int] = []
    while len(erg) < anzahl:
        if ist_primzahl(p):
            erg.append(p)
        p += 2
    return erg


def ceil_div(x: int, y: int) -> int:
    return -(-x // y)


def log_nat(n: int) -> float:
    """Natuerlicher Logarithmus auch fuer sehr grosse ganze Zahlen."""
    if n <= 0:
        raise ValueError("log einer nichtpositiven Zahl")
    k = n.bit_length()
    if k <= 1000:
        return math.log(n)
    return math.log(n >> (k - 1000)) + (k - 1000) * math.log(2)


# ---------------------------------------------------------------------------
# Lemma 2.3: Greedy-Vorlauf
# ---------------------------------------------------------------------------

def greedy_vorlauf(a: int, b: int, T: int) -> Tuple[List[int], int, int]:
    """Greedy-Schritte, bis der (ungekuerzte) Rest A/C einen Nenner C >= T hat.

    Rueckgabe: (Nenner der Greedy-Terme, A, C). A = 0 bedeutet: fertig.
    Nach Lemma 2.3 sind hoechstens 1 + ceil(log2(log T / log 2)) Schritte noetig,
    es gilt A <= a und (falls b < T) T <= C < T^2.
    """
    A, C = a, b
    terme: List[int] = []
    while A > 0 and C < T:
        z = ceil_div(C, A)
        terme.append(z)
        A, C = A * z - C, C * z
    return terme, A, C


# ---------------------------------------------------------------------------
# Lemma 2.2: Doppelte Nenner entfernen (Takenouchi)
# ---------------------------------------------------------------------------

def verschiedene_nenner(nenner: Sequence[int]) -> List[int]:
    """Macht aus einer Stammbruchsumme < 1 eine mit verschiedenen Nennern >= 2,
    ohne die Anzahl der Terme zu veraendern."""
    zaehler = Counter(nenner)
    if zaehler.get(1):
        raise ValueError("Nenner 1 ist bei Summe < 1 unmoeglich")
    doppelt = [d for d, k in zaehler.items() if k >= 2]
    while doppelt:
        d = doppelt.pop()
        while zaehler[d] >= 2:
            if d == 2:
                raise ValueError("doppelte 1/2 ist bei Summe < 1 unmoeglich")
            zaehler[d] -= 2
            p = d // 2
            if d % 2 == 0:                       # 2/(2p) = 1/(p+1) + 1/(p(p+1))
                neu = (p + 1, p * (p + 1))
            else:                                # 2/(2p+1) = 1/(p+1) + 1/((p+1)(2p+1))
                neu = (p + 1, (p + 1) * d)
            for e in neu:
                zaehler[e] += 1
                if zaehler[e] == 2:
                    doppelt.append(e)
        if zaehler[d] == 0:
            del zaehler[d]
    return sorted(zaehler.elements())


# ---------------------------------------------------------------------------
# Parameter und Hilfsnenner M (Abschnitt 4 des Papers)
# ---------------------------------------------------------------------------

@dataclass
class Parameter:
    """Konstanten der Konstruktion (in Klammern: Werte im Paper)."""
    K: float = 1.3          # Teilerlisten-Eintraege bis ~ e^{K S}            (K = 100)
    m_min: int = 6          # untere Schranke fuer m                          (-)
    m_max: int = 16         # obere Schranke fuer m (Rechenaufwand ~ 2^m)     (m = S/log S)
    R: int = 0              # Anzahl zufaelliger Bloecke T_1..T_R             (R = 1000)
                            # (R = 0: T_0 wird in allen Phasen benutzt; kuerzer)
    D0: float = 3.0         # 2^a >= S^D0, binaerer Abschluss                 (D0 = 10^5)
    D_C: int = 1            # Greedy-Vorlauf bis Nenner C >= (b M)^D_C        (C >= e^{D_C S} >= X^4)
    versuche: int = 2       # Zerlegungen n = u + (n-u) im Dichte-Schritt     (eine genuegt)
    alle_listen: bool = False   # True: in jeder Phase alle Teilerlisten nutzen
    seed: int = 2026


@dataclass
class Hilfsnenner:
    """Der Hilfsnenner M mit seinen Teilerlisten T_0, ..., T_R.

    Jede Liste wird als Folge von Paaren (c0, c1) gespeichert; der Eintrag zum
    Bitvektor I ist prod_j c_{j, I_j}. Fuer T_0 ist (c0, c1) = (1, p_j),
    fuer T_i ist (c0, c1) = (p_{i,j,0}, p_{i,j,1}).
    """
    S: float
    m: int
    a: int                       # 2^a | M
    M: int
    listen: List[List[Tuple[int, int]]]
    primzahlen_T0: List[int] = field(default_factory=list)

    @classmethod
    def konstruiere(cls, S: float, par: Parameter) -> "Hilfsnenner":
        rng = random.Random(par.seed)
        S = max(S, 3.0)
        m = int(S / math.log(S))
        m = max(par.m_min, min(par.m_max, m))
        a = max(1, math.ceil(par.D0 * math.log2(S)))
        # Paper: Primzahlen in [S^K, 2 S^K] mit m = S/log S, also m log p ~ K S.
        # Wird m aus Aufwandsgruenden gedeckelt, waehlen wir p ~ e^{K S/m}, damit
        # die Listeneintraege weiterhin bis ~ e^{K S} reichen (fuer m = S/log S
        # ist das genau S^K). Nur so gilt t > u im mittleren Bereich u <= e^S.
        log_p = max(par.K * math.log(S), par.K * S / m)
        p_min = max(3, 1 << max(1, round(log_p / math.log(2))))
        pool = primzahlen_ab(p_min, max(4 * m, m + 8))
        T0_primzahlen = sorted(rng.sample(pool, m))
        listen = [[(1, p) for p in T0_primzahlen]]
        M = (1 << a)
        for p in T0_primzahlen:
            M *= p
        for _ in range(par.R):
            block = [(rng.choice(pool), rng.choice(pool)) for _ in range(m)]
            for p0, p1 in block:
                M *= p0 * p1
            listen.append(block)
        return cls(S=S, m=m, a=a, M=M, listen=listen, primzahlen_T0=T0_primzahlen)

    def eintrag(self, liste: int, index: int) -> int:
        t = 1
        for j, (c0, c1) in enumerate(self.listen[liste]):
            t *= c1 if (index >> j) & 1 else c0
        return t

    def residuen(self, liste: int, u: int, Q: int) -> List[int]:
        """Alle h_t(u) = (-Q t) mod u fuer die 2^m Eintraege t der Liste
        (Index i <-> Bitvektor I mit I_j = Bit j von i)."""
        res = [(-Q) % u]
        for c0, c1 in self.listen[liste]:
            c0 %= u
            c1 %= u
            if c0 == 1:
                res = res + [x * c1 % u for x in res]
            else:
                res = [x * c0 % u for x in res] + [x * c1 % u for x in res]
        return res


# ---------------------------------------------------------------------------
# Der Residuen-Abstieg (Abschnitte 4 und 5)
# ---------------------------------------------------------------------------

@dataclass
class Protokoll:
    """Zaehlt, welche Stufen der Konstruktion wie viele Terme erzeugt haben."""
    greedy: int = 0
    hoch: int = 0           # Q = C, Liste T_0
    mittel: int = 0         # Q = 1, Liste T_1
    terminal: int = 0       # Q = 1, Listen T_1..T_R
    binaer: int = 0         # Zweierpotenzen von M

    def summe(self) -> int:
        return self.greedy + self.hoch + self.mittel + self.terminal + self.binaer

    def __iadd__(self, other: "Protokoll") -> "Protokoll":
        for f in ("greedy", "hoch", "mittel", "terminal", "binaer"):
            setattr(self, f, getattr(self, f) + getattr(other, f))
        return self


class Abstieg:
    """Erzeugt Zerlegungen von u/(M Q) mit Hilfe der Teiler von M."""

    def __init__(self, H: Hilfsnenner, par: Parameter, e_S: int):
        self.H = H
        self.par = par
        self.e_S = min(e_S, H.M - 1)    # Uebergang Q = C -> Q = 1 bei u <= e^S (< M)
        self.e_m = math.exp(H.m) if H.m < 700 else float("inf")
        self.binaer_grenze = 1 << H.a
        self._memo: Dict[int, Tuple[List[int], Protokoll]] = {}

    # -- Auswahl des Teilers ------------------------------------------------

    def _listen_fuer(self, u: int, Q: int) -> List[int]:
        R = len(self.H.listen) - 1
        if self.par.alle_listen:
            return list(range(R + 1))
        if Q > 1:
            return [0]                                   # hohe Stufen: T_0
        if R == 0:
            return [0]
        if u > self.e_m:
            return [1]                                   # mittlere Stufen: T_1
        return list(range(1, R + 1))                     # Terminalbereich: T_1..T_R

    def kandidaten(self, u: int, Q: int, k: int = 1) -> List[Tuple[int, int, int]]:
        """Die k kleinsten Residuen als (h, liste, index)."""
        beste: List[Tuple[int, int, int]] = []
        for li in self._listen_fuer(u, Q):
            res = self.residuen_cache(li, u, Q)
            for i in heapq.nsmallest(k, range(len(res)), key=res.__getitem__):
                beste.append((res[i], li, i))
        return heapq.nsmallest(k, beste)

    def residuen_cache(self, li: int, u: int, Q: int) -> List[int]:
        return self.H.residuen(li, u, Q)

    def schritt(self, u: int, Q: int, li: int, idx: int) -> Tuple[int, int, int]:
        """Ein Schritt der Identitaet (4.1): gibt (Nenner (M/t) z, z, h) zurueck."""
        t = self.H.eintrag(li, idx)
        z = ceil_div(Q * t, u)
        h = u * z - Q * t
        return (self.H.M // t) * z, z, h

    # -- Terminal- und Binaerbereich (Q = 1, u <= 2^a) ------------------------

    def terminal(self, u: int, tiefe: int = 0) -> Tuple[List[int], Protokoll]:
        """Kurze Zerlegung von u/M fuer kleines u: binaer oder weitere Abstiege."""
        if u == 0:
            return [], Protokoll()
        if u in self._memo:
            return self._memo[u]
        M = self.H.M
        bits = [k for k in range(u.bit_length()) if (u >> k) & 1]
        bester = ([M >> k for k in bits], Protokoll(binaer=len(bits)))
        if len(bits) > 1 and tiefe < 6:
            for h, li, idx in self.kandidaten(u, 1, k=3):
                if h >= u:
                    continue
                d, z, h = self.schritt(u, 1, li, idx)
                rest, prot = self.terminal(h, tiefe + 1)
                if 1 + len(rest) < len(bester[0]):
                    p = Protokoll(terminal=1)
                    p += prot
                    bester = ([d] + [z * x for x in rest], p)
        self._memo[u] = bester
        return bester

    # -- Gesamter Abstieg ---------------------------------------------------

    def zerlege(self, u: int, Q: int) -> Tuple[List[int], Protokoll]:
        """Zerlegung von u/(M Q) (mit u < M Q) in Stammbrueche."""
        M = self.H.M
        terme: List[int] = []
        prot = Protokoll()
        skala = 1                       # aktueller Rest = u / (M Q skala)
        schritte = 0
        while u > 0:
            schritte += 1
            if schritte > 100_000:
                raise RuntimeError("Abstieg stagniert - Parameter K/m pruefen")
            if Q > 1 and u <= self.e_S:
                # Uebergang C_j = C -> C_{j+1} = 1 (Stufe X_j <= e^S): u/(M C) = (1/C) * u/M
                skala *= Q
                Q = 1
            if Q == 1 and u <= self.binaer_grenze:
                rest, p = self.terminal(u)
                terme.extend(skala * x for x in rest)
                prot += p
                break
            h, li, idx = self.kandidaten(u, Q, k=1)[0]
            d, z, h = self.schritt(u, Q, li, idx)
            terme.append(skala * d)
            if Q > 1:
                prot.hoch += 1
            elif u > self.e_m:
                prot.mittel += 1
            else:
                prot.terminal += 1
            skala *= z
            u = h
        return terme, prot


# ---------------------------------------------------------------------------
# Hauptalgorithmus (Beweis von Satz 1.1)
# ---------------------------------------------------------------------------

@dataclass
class Ergebnis:
    a: int
    b: int
    nenner: List[int]
    protokoll: Protokoll
    hilfsnenner: Hilfsnenner
    zerlegungsart: str

    @property
    def laenge(self) -> int:
        return len(self.nenner)

    @property
    def loglog_b(self) -> float:
        return math.log(log_nat(self.b))

    def pruefe(self) -> bool:
        if len(set(self.nenner)) != len(self.nenner):
            return False
        if any(n < 2 for n in self.nenner):
            return False
        return sum(Fraction(1, n) for n in self.nenner) == Fraction(self.a, self.b)


def stammbruchzerlegung(a: int, b: int, par: Optional[Parameter] = None) -> Ergebnis:
    """Zerlegt a/b (1 <= a < b) in O(log log b) verschiedene Stammbrueche."""
    if not (1 <= a < b):
        raise ValueError("Es muss 1 <= a < b gelten.")
    par = par or Parameter()
    S = log_nat(b)

    H = Hilfsnenner.konstruiere(S, par)
    abstieg = Abstieg(H, par, e_S=b)

    # Stufe 1: Greedy-Vorlauf bis C >= T  (Lemma 2.3). Im Paper ist
    # T = e^{D_C S} mit D_C = 4 D_X, also C >= X^4 >= (A M)^4: der Faktor C
    # muss den Zaehler u <= A M weit uebertreffen, damit die Residuen
    # (-C t) mod u gleichverteilt sind. Hier: T = (b M)^{D_C}.
    T = (b * H.M) ** max(1, par.D_C)
    prefix, A, C = greedy_vorlauf(a, b, T)
    prot = Protokoll(greedy=len(prefix))

    if A == 0:
        nenner = verschiedene_nenner(prefix)
        return Ergebnis(a, b, nenner, prot, H, "nur Greedy")

    # Stufe 2-5: A/C = n/(M C) mit n = g A M.
    # Direkter Versuch (g = 1, n = A M)
    beste_terme, beste_prot = abstieg.zerlege(A * H.M, C)
    art = "direkt (n = A M)"

    # Dichte-Argument: n = g A M = u + (n - u), beide Zaehler zerlegen,
    # danach alle Nenner mit g multiplizieren (Abschnitt 2, Beweis von Satz 1.1).
    rng = random.Random(par.seed ^ (a * 1_000_003 + b))
    for versuch in range(par.versuche):
        g = 1 + versuch                       # verschiedene Vielfache g A M
        n = g * A * H.M
        if n >= H.M * C:
            break
        u = rng.randrange(1, n)
        t1, p1 = abstieg.zerlege(u, C)
        t2, p2 = abstieg.zerlege(n - u, C)
        if len(t1) + len(t2) < len(beste_terme):
            beste_terme = [g * x for x in t1 + t2]
            beste_prot = p1
            beste_prot += p2
            art = f"Dichte-Zerlegung (g = {g}, n = u + (n-u))"

    prot += beste_prot
    nenner = verschiedene_nenner(prefix + beste_terme)
    return Ergebnis(a, b, nenner, prot, H, art)


# ---------------------------------------------------------------------------
# Vergleich: klassischer Greedy-Algorithmus (Fibonacci-Sylvester)
# ---------------------------------------------------------------------------

def greedy_laenge(a: int, b: int, max_bits: int = 1 << 22) -> Optional[int]:
    """Laenge der reinen Greedy-Zerlegung (None, falls die Nenner zu gross werden;
    sie wachsen beim Greedy-Algorithmus doppelt exponentiell)."""
    x = Fraction(a, b)
    k = 0
    while x > 0:
        k += 1
        if x.denominator.bit_length() > max_bits:
            return None
        z = ceil_div(x.denominator, x.numerator)
        x -= Fraction(1, z)
    return k


# ---------------------------------------------------------------------------
# Kommandozeile
# ---------------------------------------------------------------------------

def _kurz(n: int, max_stellen: int = 40) -> str:
    s = str(n)
    if len(s) <= max_stellen:
        return s
    return f"{s[:12]}...{s[-8:]} ({len(s)} Stellen)"


def _ausgabe(erg: Ergebnis, alle: bool, vergleich: bool) -> None:
    H = erg.hilfsnenner
    p = erg.protokoll
    print(f"a/b = {_kurz(erg.a)} / {_kurz(erg.b)}")
    print(f"  S = log b = {H.S:.2f},  log log b = {erg.loglog_b:.3f},  log S = {math.log(H.S):.3f}")
    print(f"  Hilfsnenner M: {M_beschreibung(H)}")
    print(f"  Weg: {erg.zerlegungsart}")
    print(f"  Terme: {erg.laenge}  (Greedy {p.greedy}, hoch {p.hoch}, mittel {p.mittel}, "
          f"terminal {p.terminal}, binaer {p.binaer})")
    print(f"  Laenge / log log b = {erg.laenge / erg.loglog_b:.2f}")
    if vergleich:
        g = greedy_laenge(erg.a, erg.b)
        print(f"  zum Vergleich reiner Greedy-Algorithmus: {g if g is not None else 'zu gross (Nenner > 2^(2^22))'} Terme")
    print(f"  exakt geprueft (Summe = a/b, verschiedene Nenner >= 2): {'OK' if erg.pruefe() else 'FEHLER'}")
    if alle:
        for i, n in enumerate(erg.nenner, 1):
            print(f"    1/{_kurz(n, 10**9)}")
    else:
        print("  Nenner (gekuerzt): " + ", ".join(_kurz(n, 20) for n in erg.nenner[:8])
              + (" ..." if erg.laenge > 8 else ""))


def M_beschreibung(H: Hilfsnenner) -> str:
    return (f"m = {H.m} Primzahlen ~ {H.primzahlen_T0[0]}..{H.primzahlen_T0[-1]}, "
            f"{len(H.listen) - 1} Zufallsbloecke, 2^{H.a} | M, "
            f"log M = {log_nat(H.M):.1f}, je Liste 2^{H.m} = {2 ** H.m} Teiler")


def _tabelle(par: Parameter, stellen: Sequence[int], proben: int) -> None:
    rng = random.Random(par.seed)
    print(f"{'Stellen':>7} {'loglog b':>9} {'a=b-1':>6} {'Zufall max':>11} "
          f"{'Zufall mittel':>14} {'max/loglog':>11}")
    for st in stellen:
        b = rng.randrange(10 ** (st - 1), 10 ** st)
        ll = math.log(log_nat(b))
        e0 = stammbruchzerlegung(b - 1, b, par)
        assert e0.pruefe()
        laengen = []
        for _ in range(proben):
            a = rng.randrange(1, b)
            e = stammbruchzerlegung(a, b, par)
            assert e.pruefe(), (a, b)
            laengen.append(e.laenge)
        mx = max(laengen + [e0.laenge])
        print(f"{st:>7} {ll:>9.3f} {e0.laenge:>6} {max(laengen):>11} "
              f"{sum(laengen) / len(laengen):>14.2f} {mx / ll:>11.2f}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Stammbruchzerlegung a/b mit O(log log b) Termen "
                    "(Konstruktion nach OpenAI, 'Short Egyptian fractions', 2026).")
    ap.add_argument("a", nargs="?", type=int, help="Zaehler (1 <= a < b)")
    ap.add_argument("b", nargs="?", type=int, help="Nenner")
    ap.add_argument("--zufall", type=int, metavar="STELLEN",
                    help="zufaelliges a/b mit b der angegebenen Stellenzahl")
    ap.add_argument("--tabelle", action="store_true",
                    help="Experiment: Laengen fuer wachsende b gegen log log b")
    ap.add_argument("--stellen", type=int, nargs="+",
                    default=[5, 10, 20, 50, 100, 200, 400],
                    help="Stellenzahlen fuer --tabelle")
    ap.add_argument("--proben", type=int, default=5, help="Zufallszaehler je b fuer --tabelle")
    ap.add_argument("--alle", action="store_true", help="alle Nenner vollstaendig ausgeben")
    ap.add_argument("--vergleich", action="store_true", help="mit reinem Greedy vergleichen")
    ap.add_argument("--K", type=float, default=Parameter.K)
    ap.add_argument("--m-max", type=int, default=Parameter.m_max)
    ap.add_argument("--R", type=int, default=Parameter.R)
    ap.add_argument("--D0", type=float, default=Parameter.D0)
    ap.add_argument("--DC", type=int, default=Parameter.D_C)
    ap.add_argument("--versuche", type=int, default=Parameter.versuche)
    ap.add_argument("--alle-listen", action="store_true",
                    help="in jeder Phase alle Teilerlisten verwenden (kuerzer, nicht paper-treu)")
    ap.add_argument("--seed", type=int, default=Parameter.seed)
    args = ap.parse_args(argv)

    par = Parameter(K=args.K, m_max=args.m_max, R=args.R, D0=args.D0, D_C=args.DC,
                    versuche=args.versuche, alle_listen=args.alle_listen, seed=args.seed)

    if args.tabelle:
        _tabelle(par, args.stellen, args.proben)
        return 0
    if args.zufall:
        rng = random.Random(args.seed)
        b = rng.randrange(10 ** (args.zufall - 1), 10 ** args.zufall)
        a = rng.randrange(1, b)
    elif args.a is not None and args.b is not None:
        a, b = args.a, args.b
    else:
        ap.print_help()
        return 1
    erg = stammbruchzerlegung(a, b, par)
    _ausgabe(erg, args.alle, args.vergleich)
    return 0 if erg.pruefe() else 2


if __name__ == "__main__":
    sys.exit(main())
