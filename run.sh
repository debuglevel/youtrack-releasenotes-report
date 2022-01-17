#!/usr/bin/env bash

echo "= Preparing output directory..."
mkdir -p out
rm -r out/* &> /dev/null

echo "= Fetching release notes and generating Markdown..."
python3 main.py --field-name="$FIELD_NAME" --field-value="$FIELD_VALUE" --output-basename="$OUTPUT_BASENAME" "$YOUTRACK_URL" "$HUB_URL" "$TOKEN"

echo "= Converting to additional formats using pandoc..."
cp pandoc.css out/
./convert-markdown.sh