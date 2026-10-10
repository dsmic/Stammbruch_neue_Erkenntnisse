#!/usr/bin/env python3
"""Erzeugt vergleich.svg: groesste gemessene Termanzahl, neue Konstruktion gegen
Erdős 1950, aus messungen_m_paper.csv und messungen_erdos1950.csv.

    python3 diagramm.py [neu.csv] [erdos.csv] [ausgabe.svg]
"""
import csv
import sys


def lies(datei, spalte):
    return {int(z["Stellen"]): float(z[spalte]) * (float(z["loglog_b"]) if "/" in spalte else 1)
            for z in csv.DictReader(open(datei))}


def main(neu_csv="messungen_m_paper.csv", erdos_csv="messungen_erdos1950.csv",
         ausgabe="vergleich.svg"):
    neu = {k: round(v) for k, v in lies(neu_csv, "max/loglog").items()}
    erdos = {k: round(v) for k, v in lies(erdos_csv, "max").items() if k <= max(neu)}
    serien = [("Erdős 1950 (Fakultätsmethode)", "2", erdos),
              ("neu: OpenAI 2026, m = S/log S", "1", neu)]

    B, H = 720, 420
    li, re, ob, un = 56, 200, 56, 52
    x_max = 5 * ((max(neu) + 4) // 5)
    y_max = 10 * ((max(max(s.values()) for _, _, s in serien) + 9) // 10)

    def px(x):
        return li + (B - li - re) * x / x_max

    def py(y):
        return H - un - (H - ob - un) * y / y_max

    t = []
    t.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {B} {H}" '
             f'width="{B}" height="{H}" role="img" aria-labelledby="titel beschr" '
             f'font-family="system-ui, -apple-system, Segoe UI, sans-serif">')
    t.append('<title id="titel">Termanzahl im schlechtesten gemessenen Fall</title>')
    t.append('<desc id="beschr">Groesste gemessene Termanzahl je Stellenzahl von b: '
             + "; ".join(f"{k} Stellen: neu {neu.get(k, '-')}, Erdős {erdos.get(k, '-')}"
                         for k in sorted(neu)) + '</desc>')
    t.append('''<style>
  .flaeche { fill: #fcfcfb; }
  .text1 { fill: #0b0b0b; } .text2 { fill: #52514e; }
  .gitter { stroke: #e4e3df; stroke-width: 1; }
  .achse { stroke: #8f8e89; stroke-width: 1; }
  .l1 { stroke: #2a78d6; fill: none; } .l2 { stroke: #eb6834; fill: none; }
  .p1 { fill: #2a78d6; stroke: #fcfcfb; } .p2 { fill: #eb6834; stroke: #fcfcfb; }
  @media (prefers-color-scheme: dark) {
    .flaeche { fill: #1a1a19; }
    .text1 { fill: #f0efec; } .text2 { fill: #c3c2b7; }
    .gitter { stroke: #2e2e2c; } .achse { stroke: #6b6a66; }
    .l1 { stroke: #3987e5; } .l2 { stroke: #d95926; }
    .p1 { fill: #3987e5; stroke: #1a1a19; } .p2 { fill: #d95926; stroke: #1a1a19; }
  }
</style>''')
    t.append(f'<rect class="flaeche" width="{B}" height="{H}" rx="8"/>')
    t.append(f'<text class="text1" x="{li}" y="26" font-size="16" font-weight="600">'
             f'Terme im schlechtesten gemessenen Fall</text>')
    t.append(f'<text class="text2" x="{li}" y="44" font-size="12">'
             f'je b: a = b−1, b−2, b−3, b−10, ⌊(k−1)b/k⌋ und 5 zufällige Zähler</text>')
    for y in range(0, y_max + 1, 10):
        t.append(f'<line class="gitter" x1="{li}" x2="{B - re}" y1="{py(y):.1f}" y2="{py(y):.1f}"/>')
        t.append(f'<text class="text2" x="{li - 8}" y="{py(y) + 4:.1f}" font-size="11" '
                 f'text-anchor="end">{y}</text>')
    for x in range(0, x_max + 1, 10):
        t.append(f'<text class="text2" x="{px(x):.1f}" y="{H - un + 18}" font-size="11" '
                 f'text-anchor="middle">{x}</text>')
    t.append(f'<line class="achse" x1="{li}" x2="{B - re}" y1="{py(0):.1f}" y2="{py(0):.1f}"/>')
    t.append(f'<text class="text2" x="{(li + B - re) / 2:.1f}" y="{H - 12}" font-size="12" '
             f'text-anchor="middle">Stellen von b</text>')
    t.append(f'<text class="text2" x="16" y="{(ob + H - un) / 2:.1f}" font-size="12" '
             f'text-anchor="middle" transform="rotate(-90 16 {(ob + H - un) / 2:.1f})">'
             f'Anzahl Stammbrüche</text>')
    for name, cls, s in serien:
        pkt = sorted(s.items())
        pfad = " ".join(f"{'M' if i == 0 else 'L'}{px(x):.1f},{py(y):.1f}"
                        for i, (x, y) in enumerate(pkt))
        t.append(f'<path class="l{cls}" d="{pfad}" stroke-width="2" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
        for x, y in pkt:
            t.append(f'<circle class="p{cls}" cx="{px(x):.1f}" cy="{py(y):.1f}" r="4" '
                     f'stroke-width="2"><title>{name}: {x} Stellen, '
                     f'{y} Terme</title></circle>')
        xe, ye = pkt[-1]
        t.append(f'<text class="text1" x="{px(xe) + 10:.1f}" y="{py(ye) - 2:.1f}" '
                 f'font-size="12" font-weight="600">{ye} Terme</text>')
        t.append(f'<text class="text2" x="{px(xe) + 10:.1f}" y="{py(ye) + 13:.1f}" '
                 f'font-size="11">{name.split(" (")[0].split(":")[0]}</text>')
    # Legende
    lx, ly = li + 12, ob + 8
    for i, (name, cls, _) in enumerate(reversed(serien)):
        yy = ly + 18 * i
        t.append(f'<line class="l{cls}" x1="{lx}" x2="{lx + 18}" y1="{yy}" y2="{yy}" stroke-width="2"/>')
        t.append(f'<circle class="p{cls}" cx="{lx + 9}" cy="{yy}" r="4" stroke-width="2"/>')
        t.append(f'<text class="text1" x="{lx + 26}" y="{yy + 4}" font-size="12">{name}</text>')
    t.append('</svg>')
    with open(ausgabe, "w") as f:
        f.write("\n".join(t) + "\n")
    print(f"{ausgabe} geschrieben")


if __name__ == "__main__":
    main(*sys.argv[1:])
