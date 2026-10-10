#!/bin/sh
# Erzeugt aus den Markdown-Dateien druckfertige PDFs (A4).
# Benoetigt: pandoc, Node.js mit playwright und Chromium.
set -e
cd "$(dirname "$0")"
for f in Arbeitsblatt_Stammbrueche Loesungen_und_Hinweise; do
  pandoc "$f.md" -f markdown -t html5 --standalone --embed-resources \
         --css druck.css --metadata title="$f" --variable pagetitle="$f" \
         -V title= -o "$f.html"
  node pdf_drucken.js "$f.html" "$f.pdf"
  rm "$f.html"
done
