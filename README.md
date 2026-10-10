# Stammbruchzerlegung mit O(log log b) Termen

Python-Programm, das die Konstruktion aus dem Beweis von

> OpenAI, *Short Egyptian fractions*, OpenAI Math Release Preprint, 25. September 2026
> ([github.com/openai/math](https://github.com/openai/math/tree/main/preprints/Short-Egyptian-fractions-September-25-2026))

umsetzt. Dort wird die Vermutung von Erdős (1950, Erdős-Problem #304) bewiesen:

**Satz 1.1.** Es gibt absolute Konstanten c₁, c₂ > 0, so dass für alle großen b

  c₁ · log log b ≤ N(b) ≤ c₂ · log log b,

wobei N(b) = max_{1≤a<b} N(a,b) und N(a,b) die kleinste Anzahl *verschiedener*
Stammbrüche mit Summe a/b ist. Vorher bekannt: N(b) ≪ log b / log log b (Erdős 1950),
N(b) ≪ √log b (Vose 1985).

Das Programm braucht nur Python ≥ 3.8; ist `gmpy2` installiert (`pip install gmpy2`),
wird die Residuensuche damit etwa 4-mal schneller. Jede berechnete Zerlegung
wird am Ende mit exakter Bruchrechnung geprüft (Summe = a/b, alle Nenner verschieden
und ≥ 2).

## Benutzung

```bash
python3 stammbruch_loglog.py 5 121                 # a/b = 5/121
python3 stammbruch_loglog.py 5 121 --alle          # alle Nenner vollständig ausgeben
python3 stammbruch_loglog.py --zufall 50           # zufälliges a/b mit 50-stelligem b
python3 stammbruch_loglog.py --tabelle             # Experiment: Länge gegen log log b
python3 stammbruch_loglog.py --tabelle --stellen 10 20 50 100 --proben 5
python3 -m unittest -v test_stammbruch_loglog      # Tests
```

Als Bibliothek:

```python
from stammbruch_loglog import stammbruchzerlegung
e = stammbruchzerlegung(a, b)
e.nenner      # Liste der Nenner n_1 < ... < n_k
e.pruefe()    # True
```

Wichtige Optionen (in Klammern die Werte im Paper):

| Option | Bedeutung | Standard (Paper) |
|---|---|---|
| `--m-max` | Anzahl m der Primzahlen pro Teilerliste, je Liste 2^m Teiler | 16 (m = S/log S) |
| `--K` | Listeneinträge reichen bis ≈ e^{K S} (muss > 1 sein) | 1.3 (100) |
| `--R` | Anzahl der Zufallslisten T₁..T_R; bei 0 wird T₀ überall benutzt | 0 (1000) |
| `--D0` | binärer Abschluss für Zähler ≤ 2^a, 2^a ≥ S^{D0} | 3 (10⁵) |
| `--DC` | Greedy-Vorlauf, bis der Nenner C ≥ (bM)^{DC} | 1 (C ≥ e^{D_C S} ≥ X⁴) |
| `--versuche` | Versuche für den Dichte-Schritt n = u + (n−u) | 2 |
| `--alle-listen` | in jeder Phase alle Teilerlisten verwenden | aus |

## Wie der Beweis in das Programm übersetzt ist

Sei S = log b.

1. **Greedy-Vorlauf (Lemma 2.3)** – `greedy_vorlauf`.
   O(log S) Greedy-Schritte 1/z mit z = ⌈C/A⌉ (ungekürzt), bis der Rest die Form A/C
   mit A ≤ a und sehr großem Nenner C hat. Im Paper muss C ≥ e^{D_C S} ≥ X⁴ sein, damit C
   den späteren Zähler u ≤ A·M weit übertrifft; im Programm wird bis C ≥ b·M iteriert,
   was C·t > u für alle Teiler t garantiert.

2. **Hilfsnenner M (Abschnitt 4)** – `Hilfsnenner.konstruiere`.
   M = 2^a · ∏ pⱼ · ∏ p_{i,j,0} p_{i,j,1} mit m Primzahlen pro Liste.
   - T₀ = (∏_{j∈I} pⱼ)_{I⊆{1..m}} – deterministische Liste (hohe Stufen, Q = C),
   - Tᵢ = (∏ⱼ p_{i,j,Iⱼ})_I, i = 1..R – zufällige Listen (mittlere/terminale Stufen),
   jeweils 2^m Einträge, alle Teiler von M.

3. **Residuen-Abstieg (Identität (4.1), Abschnitt 5)** – `Abstieg.zerlege`.
   Für t | M, z = ⌈Qt/u⌉ und h = uz − Qt (= (−Qt) mod u) gilt

   u/(MQ) = 1/((M/t)·z) + (1/z) · h/(MQ).

   Ein Stammbruch ersetzt also den Zähler u durch das Residuum h. Das Programm wählt in
   jedem Schritt unter allen 2^m Listeneinträgen das **kleinste Residuum** (das Paper
   zeigt, dass für fast alle u genügend t ein Residuum ≤ u·e^{−ηm} liefern; die
   Minimumwahl ist die natürliche konstruktive Auswahl). Weil die Residuen
   gleichverteilt sind, spart jeder Schritt ≈ m·log 2 an log u. Mit
   log M ≈ K·m·log S und m ≈ S/log S braucht man nur **O(log S) = O(log log b)**
   Schritte – das ist der Kern des neuen Beweises.
   Sobald u ≤ e^S = b ist, wird Q = C durch Q = 1 ersetzt (alle weiteren Nenner · C).

4. **Terminal- und Binärbereich** – `Abstieg.terminal`.
   Für u ≤ 2^a ist u/M = Σ 2^k/M = Σ 1/(M/2^k) (Binärdarstellung, 2^a | M); zusätzlich
   werden noch einige Residuen-Schritte probiert und die kürzere Variante genommen.

5. **Von der dichten Menge zu jedem Zähler (Beweis von Satz 1.1, Abschnitt 2)**.
   A/C = n/(MC) mit n = g·A·M. Das Paper zeigt nur, dass *fast alle* Zähler ≤ X kurze
   Zerlegungen haben, und schreibt deshalb n = u + (n−u) mit zwei „guten“ Zählern und
   teilt danach durch g. Das Programm versucht zuerst n = A·M direkt und dann einige
   solche Aufspaltungen und nimmt die kürzeste Zerlegung.

6. **Verschiedene Nenner (Lemma 2.2, Takenouchi)** – `verschiedene_nenner`.
   2/(2p) = 1/(p+1) + 1/(p(p+1)) und 2/(2p+1) = 1/(p+1) + 1/((p+1)(2p+1)) beseitigen
   Doppelte, ohne die Termanzahl zu ändern.

Die untere Schranke (a = b−1 braucht ≥ log log b/(1+log 2) Terme) ist im Test
`test_untere_schranke` nachgerechnet.

## Was man realistisch erwarten kann

* **Korrektheit:** Jede Ausgabe ist eine exakt geprüfte Zerlegung in verschiedene
  Stammbrüche – für *jedes* 1 ≤ a < b.
* **Konstanten:** Das Paper beweist die Existenz *absoluter* Konstanten, die aber
  riesig sind (K = 100, R = 1000, D₀ = 10⁵, η = 10⁻⁴, D_M ≈ 2·10⁵) und erst für
  astronomisch große b greifen. Das Programm benutzt dieselbe Konstruktion mit kleinen,
  praktikablen Konstanten. Die gemessene Länge ist daher ein Vielfaches von log log b.
* **Rechenaufwand:** Der Beweis braucht pro Schritt eine Auswahl unter 2^m Teilern mit
  m ≈ S/log S, also ≈ b^{(log 2)/log log b} Kandidaten – subexponentiell, aber nicht
  polynomiell in log b. Das Programm begrenzt m durch `--m-max` (Standard 16, also
  65 536 Teiler pro Liste). Solange S/log S ≤ m-max ist (b bis etwa 10³⁰), folgt die
  Länge dem O(log log b)-Verhalten; für größere b wächst sie mit gedeckeltem m
  ungefähr wie S/m-max, bis man `--m-max` erhöht (jede Erhöhung um 1 verdoppelt die
  Rechenzeit pro Schritt).

## Messwerte

![Schlechtester gemessener Fall: neue Konstruktion gegen Erdős 1950](vergleich.svg)

### Neue Konstruktion mit m = ⌊S/log S⌋ wie im Paper, verglichen mit Erdős 1950

```bash
python3 stammbruch_loglog.py --tabelle --m-paper --versuche 0 --proben 5 \
        --stellen 5 10 15 20 25 30 35 40 45 50 55 --csv messungen_m_paper.csv
python3 erdos1950.py --csv messungen_erdos1950.csv
python3 diagramm.py          # erzeugt vergleich.svg
python3 auswertung.py messungen_m_paper.csv
```

Je b werden die Zähler dicht bei b zerlegt (b−1, b−2, b−3, b−10, ⌊(k−1)b/k⌋ für
k = 3, 4, 10, 100; dort läuft der Greedy-Vorlauf entlang der Sylvester-Folge am
langsamsten) und dazu 5 zufällige Zähler. „max“ ist die größte gemessene Länge, also
eine *untere* Abschätzung für den schlechtesten Fall der Konstruktion über alle a.
Das echte Maximum über alle a ist für so große b nicht berechenbar.

| Stellen | log log b | m | neu: max | bei Zähler | neu: Zufall max | neu: max / log log b | Erdős 1950: max | Erdős / log log b |
|---:|---:|---:|---:|:---|---:|---:|---:|---:|
| 5 | 2.32 | 6 | 15 | ⌊99b/100⌋ | 13 | 6.47 | 13 | 5.6 |
| 10 | 3.10 | 7 | 23 | b-10 | 18 | 7.41 | 23 | 7.4 |
| 15 | 3.54 | 9 | 23 | b-1 | 22 | 6.50 | 30 | 8.5 |
| 20 | 3.79 | 11 | 25 | b-3 | 23 | 6.60 | 38 | 10.0 |
| 25 | 4.02 | 13 | 25 | b-2 | 25 | 6.23 | 46 | 11.5 |
| 30 | 4.22 | 16 | 26 | b-10 | 25 | 6.16 | 53 | 12.6 |
| 35 | 4.39 | 18 | 26 | b-1 | 24 | 5.92 | 60 | 13.7 |
| 40 | 4.51 | 20 | 28 | b-2 | 25 | 6.20 | 66 | 14.6 |
| 45 | 4.64 | 22 | 28 | b-1 | 26 | 6.04 | 73 | 15.7 |
| 50 | 4.74 | 24 | 28 | ⌊99b/100⌋ | 26 | 5.91 | 78 | 16.5 |
| 55 | 4.84 | 26 | 28 | b-1 | 27 | 5.79 | 84 | 17.4 |
| 100 | 5.44 | – | – | – | – | – | 137 | 25.2 |
| 200 | 6.13 | – | – | – | – | – | 235 | 38.3 |
| 500 | 7.05 | – | – | – | – | – | 501 | 71.1 |
| 1000 | 7.74 | – | – | – | – | – | 894 | 115.5 |
| 2000 | 8.43 | – | – | – | – | – | 1608 | 190.6 |

Beobachtungen:

* **Neu:** max / log log b bleibt zwischen 10 und 55 Stellen bei etwa 6 (5,8–7,4); die
  Rechenzeit wächst dabei wie 2^m (55 Stellen: m = 26, ≈ 100 s pro Zerlegung mit 4 Kernen).
  Größere b sind praktisch nicht erreichbar.
* **Erdős 1950** (`erdos1950.py`, Fakultätsmethode, höchstens 2k Terme mit k! ≥ b):
  max / log log b wächst stetig (7 → 16 → 190), konstant ist dagegen
  max / (log b / log log b) ≈ 3. Schon ab etwa 15 Stellen ist die neue Konstruktion
  kürzer, bei 50 Stellen 28 gegen 78 Terme.
* **Grenzen der Aussagekraft:** log log b wächst im messbaren Bereich nur von 3,1 auf 4,8.
  Eine Anpassung L = α + β·f(b) passt für f = log log b, √log b und log b / log log b
  fast gleich gut (RMS-Fehler 0,51–0,55, `auswertung.py`). Die Messung ist mit der
  log-log-Ordnung *verträglich*, kann sie aber nicht von anderen Wachstumsraten
  unterscheiden. Das leistet nur der Beweis.
* Der Vergleich mit Erdős zeigt den Unterschied der Schranken deutlich, weil dessen
  Methode bereits im messbaren Bereich linear in log b / log log b wächst.
  Verglichen wurde nur mit Erdős 1950, nicht mit Tenenbaum–Yokota (1990, Konstante 1+ε)
  oder Vose (1985, √log b).

### Ältere Messung mit gedeckeltem m ≤ 16

`python3 stammbruch_loglog.py --tabelle --stellen 5 10 20 30 50 100 200 --proben 4`:
bis 30 Stellen ≈ 6·log log b; darüber wächst die Länge wegen des Deckels ungefähr
wie S/16 (100 Stellen: 59 Terme, 200 Stellen: 109 Terme).

## Dateien

* `stammbruch_loglog.py` – das Programm (Bibliothek + Kommandozeile)
* `test_stammbruch_loglog.py` – Tests (Lemmata 2.2, 2.3, Identität (4.1), Teilbarkeit,
  geteilte Residuensuche, vollständige Prüfung aller a/b mit b < 40, Zufallsbrüche bis
  30 Stellen, untere Schranke)
* `optimum.py` – exakte minimale Zerlegung N(a,b) und N(b) (für kleine b); `python3 optimum.py --rekorde 1000`
  reproduziert OEIS A097048: 2, 3, 5, 11, 17, 79, 733 (z. B. 732/733 braucht 7 Stammbrüche)
* `erdos1950.py` – Vergleichsverfahren: Erdős' Fakultätsmethode (log b / log log b)
* `auswertung.py` – Anpassung der gemessenen Längen an log log b, √log b, log b/log log b
* `diagramm.py`, `vergleich.svg` – Diagramm alt gegen neu
* `arbeitsblatt/` – Arbeitsblatt für Klasse 10 (Markdown und PDF) mit Lösungen;
  `arbeitsblatt/pdf_erzeugen.sh` erzeugt die PDFs neu (pandoc + Chromium)
* `messungen_*.csv` – Messreihen (`messungen_m_paper.csv` ist die maßgebliche;
  die übrigen sind ältere bzw. abgebrochene Reihen)
