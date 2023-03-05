#!/usr/bin/env bash

PLACEHOLDER_STRING="BUILD_DATE"
DATE_STRING="$(date '+%B %-d')"

while IFS= read -r line; do
    echo "${line//$PLACEHOLDER_STRING/$DATE_STRING}"
done < "src/version.ts" > "src/version.ts.tmp"

mv src/version.ts.tmp src/version.ts
