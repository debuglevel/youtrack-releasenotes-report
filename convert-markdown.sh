#!/bin/bash

echo "== Starting conversions using pandoc..."

declare -a filetypes=(".pandoc.latex.pdf" ".pandoc.html" ".pandoc.docx" ".pandoc.tex")
cd out

for filetype in "${filetypes[@]}"
do
  echo "=== Converting to $filetype..."
  # Use pandoc 2.0 or newer! pandoc < 2.0 will not convert list indentations correctly.
  pandoc -V lang=de --metadata title="$TITLE" --toc -s --css pandoc.css intermediate.md -o "${OUTPUT_BASENAME}$filetype"
  echo "=== Converted to $filetype"
done


