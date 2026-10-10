#!/usr/bin/env python3
"""
Vergleichsverfahren: Erdős' Fakultaetsmethode (1950), N(b) << log b / log log b
================================================================================

P. Erdős, "Az 1/x_1 + 1/x_2 + ... + 1/x_n = a/b egyenlet egész számú
megoldásairól", Mat. Lapok 1 (1950), 192-210 (Theorem 1, Section 1).

Konstruktion:
  * Waehle k minimal mit k! >= b und setze L = k!.
  * Mit q = floor(a L / b), r = a L - q b gilt   a/b = q/L + r/(b L),
    wobei 0 <= q < L und 0 <= r < b <= L.
  * Erdős' Lemma: jedes n < k! ist Summe von hoechstens k verschiedenen Teilern
    von k!.  Konstruktiv: n = k q' + r' mit 0 <= r' < k; zerlege q' < (k-1)!
    rekursiv mit Teilern d von (k-1)!; dann sind r' und die k d verschiedene
    Teiler von k!.
  * Jeder Teiler d liefert d/L = 1/(L/d) bzw. d/(bL) = 1/(bL/d).

Das ergibt hoechstens 2k Terme, und k ~ log b / log log b.  Der Aufwand ist
polynomiell in log b, das Verfahren laeuft also auch fuer b mit Tausenden Stellen.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import time
from fractions import Fraction
from typing import List, Sequence

from stammbruch_loglog import log_nat, spezielle_zaehler, verschiedene_nenner


def teiler_der_fakultaet(n: int, k: int) -> List[int]:
    """Verschiedene Teiler von k! mit Summe n (0 <= n < k!), hoechstens k Stueck."""
    teile: List[int] = []
    faktor = 1                       # Produkt der bereits abgespaltenen k, k-1, ...
    while n > 0:
        if k <= 1:
            raise ValueError("n >= k!")
        n, r = divmod(n, k)
        if r:
            teile.append(faktor * r)
        faktor *= k
        k -= 1
    return teile


def erdos_zerlegung(a: int, b: int) -> List[int]:
    """Zerlegung von a/b (1 <= a < b) in verschiedene Stammbrueche nach Erdős 1950."""
    if not (1 <= a < b):
        raise ValueError("Es muss 1 <= a < b gelten.")
    k, L = 1, 1
    while L < b:
        k += 1
        L *= k
    q, r = divmod(a * L, b)
    nenner = [L // d for d in teiler_der_fakultaet(q, k)]
    nenner += [b * L // d for d in teiler_der_fakultaet(r, k)]
    return verschiedene_nenner(nenner)


def _pruefe(a: int, b: int, nenner: Sequence[int]) -> bool:
    return (len(set(nenner)) == len(nenner) and min(nenner) >= 2
            and sum(Fraction(1, n) for n in nenner) == Fraction(a, b))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Erdős' Fakultaetsmethode (1950) zum Vergleich.")
    ap.add_argument("--stellen", type=int, nargs="+",
                    default=[5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 100, 200, 500, 1000])
    ap.add_argument("--proben", type=int, default=5)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--csv", metavar="DATEI")
    args = ap.parse_args(argv)
    rng = random.Random(args.seed)
    kopf = "Stellen,S,loglog_b,k,max,mittel,max/loglog,max/(S/logS),Sek/Zerlegung"
    print(f"{'Stellen':>7} {'loglog b':>9} {'k':>4} {'max':>5} {'mittel':>7} "
          f"{'max/loglog':>10} {'max/(S/logS)':>12} {'Sek':>7}", flush=True)
    zeilen = [kopf]
    for st in args.stellen:
        b = rng.randrange(10 ** (st - 1), 10 ** st)
        S = log_nat(b)
        zaehler = list(spezielle_zaehler(b).values())
        zaehler += [rng.randrange(1, b) for _ in range(args.proben)]
        t0 = time.time()
        laengen = []
        for a in zaehler:
            n = erdos_zerlegung(a, b)
            if st <= 200:
                assert _pruefe(a, b, n), (a, b)
            laengen.append(len(n))
        sek = (time.time() - t0) / len(zaehler)
        k = 1
        while math.lgamma(k + 1) < S:
            k += 1
        mx, mittel, ll = max(laengen), sum(laengen) / len(laengen), math.log(S)
        print(f"{st:>7} {ll:>9.3f} {k:>4} {mx:>5} {mittel:>7.2f} {mx / ll:>10.2f} "
              f"{mx / (S / math.log(S)):>12.2f} {sek:>7.3f}", flush=True)
        zeilen.append(f"{st},{S:.4f},{ll:.4f},{k},{mx},{mittel:.4f},{mx / ll:.4f},"
                      f"{mx / (S / math.log(S)):.4f},{sek:.4f}")
    if args.csv:
        with open(args.csv, "w") as f:
            f.write("\n".join(zeilen) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
