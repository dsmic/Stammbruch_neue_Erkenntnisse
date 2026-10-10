#!/usr/bin/env python3
"""
Wie haengt die Laenge der Konstruktion von den Parametern des Beweises ab?
==========================================================================

Die Konstruktion aus "Short Egyptian fractions" hat drei Stellschrauben, die
die Konstante vor log log b bestimmen:

  K    Groesse der Primzahlen (~ S^K); Listeneintraege t reichen bis e^{K S}.
  R    Zahl der Zufallslisten T_1..T_R; M = 2^a * prod p_j * prod p_{i,j,0} p_{i,j,1},
       also log M ~ (2R+1) K S.
  eta  garantierte Abstiegsrate: der Beweis zeigt nur, dass es ein t mit
       h <= u * e^{-eta m} gibt (eta = 10^-4 im Paper).

Das Hauptprogramm nimmt in jedem Schritt das *kleinste* Residuum ("beste Wahl").
Hier gibt es zusaetzlich die "Paper-Regel": irgendein zulaessiges t mit
h <= u * e^{-eta m}, zufaellig gewaehlt. Findet sich keins, ist u eine
"Ausnahme" (im Beweis: Element der Ausnahmemenge H_j); dann wird das kleinste
Residuum genommen und die Ausnahme gezaehlt.

Erwartung (Heuristik): Der Abstieg muss log(A M) ~ D S mit D = (2R+1) K + 1 abbauen.
Pro Schritt gewinnt die beste Wahl etwa m log 2, eine zufaellige zulaessige Wahl
etwa eta m + 1; der Beweis darf nur mit dem garantierten Gewinn eta m rechnen.
Mit m = S / log S folgt

    Abstiegsschritte ~ D * S / (m log 2) = D * log S / log 2      (beste Wahl)
    Beweis-Garantie  <= D * S / (eta m)  = D * log S / eta         (Paper-Regel)

also immer ein Vielfaches von log S = log log b, mit sehr verschiedenem Faktor.

    python3 konstruktion/parameter_experiment.py            # alle drei Versuchsreihen
    python3 konstruktion/parameter_experiment.py --stellen 25 --proben 6
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys
import time
from fractions import Fraction
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import stammbruch_loglog as sb  # noqa: E402


class PaperAbstieg(sb.Abstieg):
    """Abstieg mit waehlbarer Auswahlregel: beste Wahl (eta=None) oder Paper-Regel."""

    def __init__(self, H, par, e_S, eta: Optional[float], rng: random.Random):
        super().__init__(H, par, e_S)
        self.eta = eta
        self.rng = rng
        self.ausnahmen = 0
        self.schritte = 0

    def kandidaten(self, u: int, Q: int, k: int = 1) -> List[Tuple[int, int, int]]:
        if k != 1 or self.eta is None:
            return super().kandidaten(u, Q, k)
        self.schritte += 1
        grenze = u * math.exp(-self.eta * self.H.m)
        zulaessig = []
        bestes = None
        for li in self._listen_fuer(u, Q):
            res = self.H.residuen(li, u, Q)
            for i, h in enumerate(res):
                if h <= grenze:
                    zulaessig.append((h, li, i))
                if bestes is None or h < bestes[0]:
                    bestes = (h, li, i)
        if zulaessig:
            return [self.rng.choice(zulaessig)]
        self.ausnahmen += 1
        return [bestes]


def zerlegung(a: int, b: int, par: sb.Parameter, eta: Optional[float]) -> Tuple[int, int, int, int]:
    """Konstruktion wie im Hauptprogramm (direkter Weg n = A M), mit waehlbarer Regel.

    Rueckgabe: (Laenge, Greedy-Terme, Abstiegsschritte, Ausnahmen)."""
    S = sb.log_nat(b)
    H = sb.Hilfsnenner.konstruiere(S, par)
    ab = PaperAbstieg(H, par, b, eta, random.Random(a ^ b))
    prefix, A, C = sb.greedy_vorlauf(a, b, (b * H.M) ** max(1, par.D_C))
    terme: List[int] = []
    if A:
        terme, _ = ab.zerlege(A * H.M, C)
    nenner = sb.verschiedene_nenner(prefix + terme)
    assert sum(Fraction(1, n) for n in nenner) == Fraction(a, b)
    assert len(set(nenner)) == len(nenner)
    return len(nenner), len(prefix), len(terme), ab.ausnahmen


def reihe(titel, varianten, brueche, S, m):
    print(f"\n### {titel}\n")
    print("| Variante | Abstieg erwartet | Abstieg gemessen (Mittel) | Beweis-Garantie "
          "| Länge Mittel | Länge max | Länge max / log log b | Ausnahmen |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, par, eta in varianten:
        t0 = time.time()
        erg = [zerlegung(a, b, par, eta) for a, b in brueche]
        D = (2 * par.R + 1) * par.K + 1           # log(A M) ~ D * S
        # erwarteter Gewinn pro Schritt (in log u): beste Wahl ~ m log 2,
        # zufaellige zulaessige Wahl ~ eta m + 1 (Residuum gleichverteilt unter der Grenze)
        gewinn = m * math.log(2) if eta is None else eta * m + 1
        vorhersage = D * S / gewinn
        garantie = f"{D * S / (eta * m):.0f}" if eta else "–"
        laengen = [e[0] for e in erg]
        abstieg = sum(e[2] for e in erg) / len(erg)
        print(f"| {name} | {vorhersage:.0f} | {abstieg:.1f} | {garantie} | {sum(laengen) / len(laengen):.1f} "
              f"| {max(laengen)} | {max(laengen) / math.log(S):.1f} | {sum(e[3] for e in erg)} |",
              flush=True)
        _ = time.time() - t0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--stellen", type=int, default=20)
    ap.add_argument("--proben", type=int, default=5, help="zufaellige Zaehler (zusaetzlich a = b-1)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)

    rng = random.Random(args.seed)
    b = rng.randrange(10 ** (args.stellen - 1), 10 ** args.stellen)
    brueche = [(b - 1, b)] + [(rng.randrange(1, b), b) for _ in range(args.proben)]
    S = sb.log_nat(b)
    basis = dict(m_paper=True, versuche=0, prozesse=1)
    m = sb.Hilfsnenner.konstruiere(S, sb.Parameter(**basis)).m
    print(f"b mit {args.stellen} Stellen, S = log b = {S:.1f}, log log b = {math.log(S):.2f}, "
          f"m = {m}, {len(brueche)} Zähler (b−1 und {args.proben} zufällige)")

    reihe("Reihe 1: Primzahlgröße K (R = 0, beste Wahl)",
          [(f"K = {K}", sb.Parameter(K=K, R=0, **basis), None) for K in (1.3, 2, 4, 8)],
          brueche, S, m)
    reihe("Reihe 2: Zahl der Zufallslisten R (K = 2, beste Wahl)",
          [(f"R = {R}", sb.Parameter(K=2, R=R, **basis), None) for R in (0, 1, 2, 4)],
          brueche, S, m)
    reihe("Reihe 3: Auswahlregel (K = 1.3, R = 0)",
          [("beste Wahl", sb.Parameter(K=1.3, R=0, **basis), None)]
          + [(f"Paper-Regel η = {eta}", sb.Parameter(K=1.3, R=0, **basis), eta)
             for eta in (0.5, 0.25, 0.1, 0.05)],
          brueche, S, m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
