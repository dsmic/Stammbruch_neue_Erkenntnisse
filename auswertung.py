#!/usr/bin/env python3
"""Auswertung einer Messreihe (CSV von `stammbruch_loglog.py --tabelle --csv`).

Passt die mittlere Laenge L(b) an drei Modelle  L = alpha + beta * f(b)  an,
mit f = log log b (neue Schranke), sqrt(log b) (Vose 1985) und
log b / log log b (Erdős 1950), und gibt die Restfehler aus.
"""
import csv
import math
import sys


def anpassen(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    beta = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    alpha = my - beta * mx
    rms = math.sqrt(sum((y - alpha - beta * x) ** 2 for x, y in zip(xs, ys)) / n)
    return alpha, beta, rms


def main(datei, ab_stellen=10):
    zeilen = [z for z in csv.DictReader(open(datei)) if int(z["Stellen"]) >= ab_stellen]
    S = [float(z["S"]) for z in zeilen]
    # mittlere Laenge ueber a = b-1 und die Zufallszaehler
    L = [float(z["mittel/loglog"]) * float(z["loglog_b"]) for z in zeilen]
    modelle = {
        "log log b": [math.log(s) for s in S],
        "sqrt(log b)": [math.sqrt(s) for s in S],
        "log b / log log b": [s / math.log(s) for s in S],
    }
    print(f"{len(zeilen)} Messpunkte, Stellen {zeilen[0]['Stellen']}..{zeilen[-1]['Stellen']}")
    print(f"{'Modell':<20} {'alpha':>8} {'beta':>8} {'RMS-Fehler':>11}")
    for name, xs in modelle.items():
        a, b, r = anpassen(xs, L)
        print(f"{name:<20} {a:>8.2f} {b:>8.3f} {r:>11.3f}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10)
