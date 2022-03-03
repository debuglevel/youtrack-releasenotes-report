#!/usr/bin/env bash

echo "= Preparing output directory..."
mkdir -p out
rm -r out/* &> /dev/null

echo "= Fetching content and generating Markdown..."
python3 main.py --field="$FIELD" --query="$QUERY" --output-basename="$OUTPUT_BASENAME" "$YOUTRACK_URL" "$HUB_URL" "$TOKEN"

echo "= Converting to additional formats using pandoc..."
cp pandoc.css out/
./convert-markdown.sh