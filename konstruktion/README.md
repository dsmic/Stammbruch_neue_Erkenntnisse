# Über die Konstruktion: was das Programm macht und woher c₂ kommt

## Kurzantwort

Das Programm benutzt **denselben Mechanismus** wie der Beweis, aber **andere Parameter** und
eine **andere Auswahlregel**. Beides ergibt Längen der Form *c · log log b*. Nur die
Konstante c ist völlig verschieden:

| Variante | Konstante vor log log b (nur der Abstieg) |
|---|---:|
| Programm (K = 1,3, R = 0, beste Wahl) | ≈ 3–4, mit Greedy-Vorlauf gemessen ≈ 6 |
| Paper-Parameter (K = 100, R = 1000), aber beste Wahl | ≈ 3 · 10⁵ (hochgerechnet) |
| Paper-Parameter und Paper-Regel (Garantie η = 10⁻⁴) | ≈ 2 · 10⁹, mit allen Faktoren ≈ 10¹⁰ |

„Log log b“ ist also keine Aussage über die Größe, sondern über das **Wachstum**: Wie die
Länge mit b zunimmt. Die Konstante davor kann 6 oder 10¹⁰ sein. Das Programm misst die 6,
der Beweis garantiert die 10¹⁰.

## Der gemeinsame Mechanismus

Für einen Teiler t des Hilfsnenners M und z = ⌈Qt/u⌉, h = uz − Qt gilt

  u/(MQ) = 1/((M/t)·z) + (1/z) · h/(MQ).

Ein Stammbruch ersetzt also den Zähler u durch das Residuum h = (−Qt) mod u. Wie viele
Schritte braucht man, bis u = 0 ist?

* **Zu bewältigen:** Der Startzähler ist n = A·M. Mit log M ≈ (2R+1)·K·S und A < b ist
  log n ≈ D · S mit **D = (2R+1)·K + 1** (S = log b).
* **Gewinn pro Schritt:** Es stehen 2^m Teiler zur Wahl (Produkte aus m Primzahlen). Sind
  die Residuen gleichverteilt, ist das kleinste etwa u/2^m: Man gewinnt **m · log 2** an
  log u.
* **Schritte:** D·S / (m·log 2). Mit **m = S / log S** (wie im Paper) wird daraus

  **D · log S / log 2 = D/log 2 · log log b.**

Das ist der Kern des Beweises: Weil m fast so groß wie S ist, frisst jeder Schritt einen
festen Anteil der *Stellenzahl der Stellenzahl*. Der Greedy-Vorlauf kostet ebenfalls
O(log S) Schritte.

## Was das Paper festlegt und was das Programm macht

| | Paper | Programm (`stammbruch_loglog.py`) |
|---|---|---|
| Primzahlen pro Liste m | ⌊S/log S⌋ | gleich mit `--m-paper`; sonst gedeckelt (16) |
| Primzahlgröße | S^K mit **K = 100** | S^K mit **K = 1,3** |
| Zufallslisten | **R = 1000** | **R = 0** (nur die feste Liste T₀) |
| Binärbereich | u ≤ S^{D₀}, **D₀ = 10⁵** | D₀ = 3 |
| Greedy-Vorlauf bis | C ≥ e^{D_C·S}, D_C ≈ 8 · 10⁵ | C ≥ b·M |
| Auswahl des Teilers t | **irgendein** t mit h ≤ u·e^{−ηm}, **η = 10⁻⁴**; dass es eins gibt, ist bewiesen (außer für eine kleine Ausnahmemenge) | **das** t mit dem kleinsten Residuum |
| Dichte-Schritt n = u + (n−u) | immer (nur für *fast alle* Zähler ist ein kurzer Abstieg bewiesen) | zuerst direkt, Aufspaltung optional |
| Ergebnis | garantiert für alle a/b ab einer Schwelle b₀ | exakt geprüft, Länge nur beobachtet |

## Messung: die Formel stimmt

`parameter_experiment.py` dreht an jeweils einer Stellschraube (vollständige Tabellen:
[ergebnis_20_stellen.md](ergebnis_20_stellen.md), [ergebnis_30_stellen.md](ergebnis_30_stellen.md)).
Auszug für 30-stellige b (m = 16, a = b−1 und 5 zufällige Zähler):

| Variante | D = (2R+1)K+1 | Abstieg erwartet | Abstieg gemessen | Länge max / log log b |
|---|---:|---:|---:|---:|
| K = 1,3, R = 0 | 2,3 | 14 | 16,5 | 5,9 |
| K = 8, R = 0 | 9 | 56 | 54,2 | 15,4 |
| K = 2, R = 4 | 19 | 117 | 109,8 | 29,1 |
| Paper-Regel η = 0,1 (K = 1,3) | 2,3 | 61 | 63,2 | 17,7 |
| Paper-Regel η = 0,05 (K = 1,3) | 2,3 | 88 | 95,8 | 25,1 |

* Die Abstiegslänge ist proportional zu D: Größere Primzahlen (K) und mehr Zufallslisten
  (R) machen M größer, und der Abstieg muss entsprechend mehr abbauen.
* Mit der Paper-Regel wird es umso länger, je kleiner η ist. Wählt man zufällig unter den
  zulässigen t, gewinnt man im Mittel ηm + 1 pro Schritt; die **Beweis-Garantie** darf nur
  mit ηm rechnen (Spalte „Beweis-Garantie“ in den Ergebnisdateien, z. B. 197 statt 96
  gemessen bei η = 0,05).
* Die Spalte „Ausnahmen“ zählt Zähler, für die *kein* t die Paper-Bedingung erfüllt. Das ist
  genau die Ausnahmemenge H_j, die der Beweis mit Divisor-Momenten und der
  Hölder-Ungleichung klein hält. Bei η = 0,5 und 20 Stellen traten 2 Ausnahmen auf.

## Hochrechnung auf die Parameter des Papers

Mit K = 100, R = 1000 ist D = 200 101.

* **Beste Wahl:** D / log 2 ≈ **2,9 · 10⁵** · log log b Abstiegsschritte.
* **Paper-Regel, Garantie:** D / η ≈ **2 · 10⁹** · log log b. Im Paper steht dafür
  K_d = 3·D_X/η ≈ 6 · 10⁹ (mit etwas Spielraum), dazu der Faktor 2 aus der Aufspaltung
  n = u + (n−u). Das ergibt **c₂ ≈ 10¹⁰**.

Ausführen lässt sich die Konstruktion mit Paper-Parametern nicht: Schon bei 30 Stellen hätte
M rund 6 Millionen Stellen, und es wären über eine Million Abstiegsschritte nötig.

## Warum braucht der Beweis so große Werte?

Der Beweis muss für **jeden** Zähler garantieren, dass genügend kleine Residuen existieren.
Jede Garantie kostet:

* **K = 100 (große Primzahlen):** Die Residuen (−Ct) mod u sollen gleichverteilt sein. Das
  wird mit Fourier-Analysis gezeigt (Erdős–Turán-Ungleichung, Abschätzung von Σ e(Z/n) nach
  van der Corput). Dafür müssen die Teiler t sehr viel größer als die Zähler u sein, und
  die Ersparnis in diesen Summen ist winzig.
* **R = 1000 Zufallslisten:** Für die kleinen Zähler (Terminalbereich) soll *jeder* Zähler
  abgedeckt sein, nicht nur fast jeder. Mit vielen unabhängigen Zufallslisten wird die
  Wahrscheinlichkeit, dass ein Zähler in allen Listen durchfällt, klein genug, um über alle
  Zähler zu summieren.
* **η = 10⁻⁴:** Aus der Gleichverteilung folgt nur, dass ein Anteil e^{−ηm} der Teiler ein
  Residuum unter u·e^{−ηm} liefert. Je größer η, desto stärker müssten die Fourier-Abschätzungen
  sein.
* **D_C ≈ 8 · 10⁵:** Der Faktor C muss die Zähler weit übertreffen, damit die Phasen
  Ct/u stark genug oszillieren.
* **Die Aufspaltung n = u + (n−u):** Bewiesen ist der kurze Abstieg nur für *fast alle* Zähler.

Das Programm braucht diese Garantien nicht, weil es jede Zerlegung am Ende exakt prüft.
Es kann aber nicht ausschließen, dass mit seinen kleinen Parametern irgendwo ein Zähler
deutlich länger braucht. Diese Lücke zwischen „beobachtet ≈ 6“ und „bewiesen ≈ 10¹⁰“
schließt nur ein besserer Beweis.

## Mögliche nächste Schritte

* **Ausnahmen messen:** Wie oft liefert die beste Wahl ein Residuum über u·e^{−ηm}, als
  Funktion von η, m und K? Das wäre eine empirische Schätzung der Ausnahmemengen H_j.
* **Kleinstes sicheres K:** Ab welchem K stagniert der Abstieg nie (t muss größer als u
  sein)? Mit K < 1 bricht er erkennbar ein.
* **Vergleich mit der direkteren Methode** des Papers für a = b−1 (Konstante 257/log 2).
