#!/usr/bin/env python3
"""
Exakte minimale Stammbruchzerlegung N(a, b) und N(b) = max_a N(a, b)
====================================================================

Iterative Vertiefung: es wird k = 1, 2, 3, ... versucht. Bei k Termen mit
n_1 < n_2 < ... gilt fuer den ersten Nenner  b/a < n_1 <= k b/a.  Die letzten
zwei Terme werden exakt bestimmt: aus p/q = 1/x + 1/y folgt
(p x - q)(p y - q) = q^2, also durchlaeuft man die Teiler von q^2.

Der Aufwand waechst doppelt exponentiell mit der Termanzahl: einzelne Brueche
sind bis etwa 10 Stellen machbar, N(b) (alle a < b) bis b ~ 10^3 - 10^4.

    python3 optimum.py 77 79          # N(77, 79) mit Zerlegung
    python3 optimum.py --rekorde 3000 # kleinste b mit neuem Rekord N(b)
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from fractions import Fraction
from functools import lru_cache
from typing import List, Optional, Tuple

try:
    from sympy import factorint
except ImportError:                       # einfache Ersatz-Faktorisierung
    def factorint(n: int) -> dict:
        f, p = {}, 2
        while p * p <= n:
            while n % p == 0:
                f[p] = f.get(p, 0) + 1
                n //= p
            p += 1 if p == 2 else 2
        if n > 1:
            f[n] = f.get(n, 0) + 1
        return f


@lru_cache(maxsize=200_000)
def _faktoren(q: int) -> Tuple[Tuple[int, int], ...]:
    return tuple(factorint(q).items())


def _teiler_unter(faktoren, grenze: int) -> List[int]:
    ds = [1]
    for p, e in faktoren:
        neu = []
        for d in ds:
            x = d
            for _ in range(e + 1):
                if x >= grenze:
                    break
                neu.append(x)
                x *= p
        ds = neu
    return ds


def _zwei(p: int, q: int, lo: int) -> Optional[List[int]]:
    """1/x + 1/y = p/q mit lo <= x < y."""
    for X in _teiler_unter(tuple((pr, 2 * e) for pr, e in _faktoren(q)), q):
        if (X + q) % p:
            continue
        Y = q * q // X
        if (Y + q) % p:
            continue
        x = (X + q) // p
        if x >= lo:
            return [x, (Y + q) // p]
    return None


def _suche(p: int, q: int, k: int, lo: int) -> Optional[List[int]]:
    g = math.gcd(p, q)
    p, q = p // g, q // g
    if k == 1:
        return [q // p] if q % p == 0 and q // p >= lo else None
    if k == 2:
        return _zwei(p, q, lo)
    for x in range(max(lo, q // p + 1), k * q // p + 1):
        r = _suche(p * x - q, q * x, k - 1, x + 1)
        if r:
            return [x] + r
    return None


def optimale_zerlegung(a: int, b: int, k_max: int = 20) -> List[int]:
    """Kuerzeste Zerlegung von a/b (0 < a/b < 1) in verschiedene Stammbrueche."""
    if not (1 <= a < b):
        raise ValueError("Es muss 1 <= a < b gelten.")
    for k in range(1, k_max + 1):
        r = _suche(a, b, k, 2)
        if r:
            return r
    raise RuntimeError("k_max zu klein")


def braucht_mehr_als(a: int, b: int, k: int) -> bool:
    """True, wenn a/b nicht mit hoechstens k Stammbruechen darstellbar ist."""
    return all(_suche(a, b, j, 2) is None for j in range(1, k + 1))


def N(b: int) -> Tuple[int, int]:
    """(N(b), Zaehler a < b mit N(a, b) = N(b))."""
    return max((len(optimale_zerlegung(a, b)), a) for a in range(1, b))


def rekorde(b_max: int) -> None:
    """Kleinste b, bei denen N(b) einen neuen Hoechstwert erreicht."""
    rekord, t0 = 0, time.time()
    for b in range(2, b_max + 1):
        for a in range(b - 1, 0, -1):            # Zaehler dicht bei b sind meist am schwersten
            if braucht_mehr_als(a, b, rekord):
                z = optimale_zerlegung(a, b)
                rekord = len(z)
                print(f"N({b}) = {rekord}:  {a}/{b} = " + " + ".join(f"1/{n}" for n in z)
                      + f"   [{time.time() - t0:.1f} s]", flush=True)
                break


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exakte minimale Stammbruchzerlegungen.")
    ap.add_argument("a", nargs="?", type=int)
    ap.add_argument("b", nargs="?", type=int)
    ap.add_argument("--rekorde", type=int, metavar="B_MAX",
                    help="kleinste b mit neuem Rekordwert N(b), bis B_MAX")
    args = ap.parse_args(argv)
    if args.rekorde:
        rekorde(args.rekorde)
        return 0
    if args.a is None or args.b is None:
        ap.print_help()
        return 1
    z = optimale_zerlegung(args.a, args.b)
    assert sum(Fraction(1, n) for n in z) == Fraction(args.a, args.b)
    print(f"N({args.a}, {args.b}) = {len(z)}:  " + " + ".join(f"1/{n}" for n in z))
    return 0


if __name__ == "__main__":
    sys.exit(main())
