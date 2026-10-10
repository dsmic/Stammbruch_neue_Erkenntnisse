# Literaturnotizen

Kurznotizen zu Arbeiten, die für die Einordnung des Projekts gelesen wurden. Die PDFs selbst
liegen aus Urheberrechtsgründen nicht im Repository.

## OpenAI (2026): Short Egyptian fractions

OpenAI Math Release Preprint, 25.09.2026,
[github.com/openai/math](https://github.com/openai/math/tree/main/preprints/Short-Egyptian-fractions-September-25-2026).

* Satz 1.1: c₁ · log log b ≤ N(b) ≤ c₂ · log log b für b ≥ b₀ (Erdős-Problem #304).
  c₂ wird ausdrücklich nicht quantifiziert („without quantifying the constant c₂“).
* Korollar 1.3 (Erdős-Problem #293): exp(exp(k/600)) ≤ v(k) ≤ 1 + k^(2^(k−1)), mit der
  expliziten Längenkonstante 257/log 2 für Zerlegungen von 1 mit vorgeschriebenem Nenner m
  (also insbesondere für (m−1)/m).
* Lean-Formalisierung vorhanden (`lean/docs/025.md` im OpenAI-Repository).
* Details zur Konstruktion: siehe `../konstruktion/README.md`.

## W. van Doorn, Q. Tang (2025/26): The smallest denominator not contained in a unit fraction decomposition of 1 with fixed length

[arXiv 2512.22083](https://arxiv.org/abs/2512.22083), v2 vom 24.05.2026.

* Hauptsatz: v(k) ≥ e^{ck²} mit c = min(log 2 / 432², 1/(433·C)²), C die Konstante aus
  Voses Lemma, also ebenfalls nicht beziffert.
* **Lemma 2.2 (Vose 1985):** Es gibt α ∈ ℕ und Primzahlen 5 ≤ p₁ < p₂ < …, sodass mit
  N_K = 4^{αK²} · (p₁⋯p_K)² gilt: Für jedes a/b ∈ (0, 1) gibt es K und Teiler d_i, d′_j von
  N_K mit a/b = Σ 1/(N_K/d_i) + Σ 1/(b·N_K/d′_j) und r + s ≤ C·√log b,
  „for some absolute constant C“. Weder C noch α werden angegeben.
* Struktur wie bei Erdős 1950 und OpenAI 2026: ein gemeinsamer Hilfsnenner mit sehr vielen
  Teilern. Wie die Teiler gefunden werden, stammt aus Vose (1984), „Integers with
  consecutive divisors in small ratio“. Ob das in Polynomialzeit geht, ist ohne die
  Originale nicht zu entscheiden (N_K hat etwa (2αK²+1)·3^K Teiler, K ≈ √log b).
* Schlussbemerkung: „The current best known upper bound is by Vose … If N(b) ≪ log log b
  holds, it seems likely that our lower bound on v(k) can be improved to e^{e^{ck}}.“
  Genau das hat das OpenAI-Paper einige Monate später bewiesen, mit c = 1/600.
* Zusammenhang #293 ↔ #304: Aus b < v(k) folgt N(b−1, b) ≤ k − 1.

## Bettin, Grenié, Molteni, Sanna (2025): A lower bound for the number of Egyptian fractions

[arXiv 2509.10030](https://arxiv.org/abs/2509.10030), nur über Suchergebnisse bekannt.

* Zählt die Brüche, die als Summe verschiedener Stammbrüche mit Nennern ≤ N darstellbar
  sind (|E_N|), verbessert den führenden Faktor einer Schranke von Bleicher–Erdős von 1 auf
  fast 2. Betrifft nicht die Länge N(b).

## Nicht eingesehen

* M. D. Vose, Egyptian fractions, Bull. London Math. Soc. 17 (1985), 21–24. Würde die
  Konstante C in N(b) ≤ C·√log b und die Laufzeit klären.
* M. D. Vose, Integers with consecutive divisors in small ratio, J. Number Theory 19 (1984),
  233–238.
* G. Tenenbaum, H. Yokota, Length and denominators of Egyptian fractions III,
  J. Number Theory 35 (1990). Konstante 1 + ε laut Zitat im OpenAI-Paper.
