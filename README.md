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

Das Programm hat keine Abhängigkeiten außer Python ≥ 3.8. Jede berechnete Zerlegung
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

`python3 stammbruch_loglog.py --tabelle --stellen 5 10 20 30 50 100 200 --proben 4`
(Standardparameter, m ≤ 16; „Zufall“ = 4 zufällige Zähler a):

| Stellen von b | log log b | a = b−1 | Zufall max | Zufall Mittel | max / log log b |
|---:|---:|---:|---:|---:|---:|
| 5   | 2.32 | 13  | 13  | 6.5   | 5.6  |
| 10  | 3.13 | 21  | 20  | 19.0  | 6.7  |
| 20  | 3.83 | 24  | 22  | 20.8  | 6.3  |
| 30  | 4.23 | 25  | 23  | 22.5  | 5.9  |
| 50  | 4.74 | 35  | 34  | 32.8  | 7.4  |
| 100 | 5.44 | 59  | 59  | 57.0  | 10.9 |
| 200 | 6.13 | 109 | 107 | 106.5 | 17.8 |

Bis etwa 30 Stellen (dort ist S/log S ≤ 16, also m wie im Paper) bleibt das Verhältnis
Länge / log log b konstant bei ≈ 6. Darüber wirkt der Deckel `--m-max 16`; mit größerem
m sinkt die Länge wieder, z. B. bei einem 50-stelligen b: m ≤ 16 → 33 Terme (2 s),
m ≤ 18 → 32 Terme (9 s), m ≤ 20 → 28 Terme (34 s).

## Dateien

* `stammbruch_loglog.py` – das Programm (Bibliothek + Kommandozeile)
* `test_stammbruch_loglog.py` – Tests (Lemmata 2.2, 2.3, Identität (4.1), Teilbarkeit,
  vollständige Prüfung aller a/b mit b < 40, Zufallsbrüche bis 30 Stellen, untere Schranke)
