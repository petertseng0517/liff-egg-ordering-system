#!/bin/bash
# 將 Markdown 轉成 PDF（保留中文與 emoji），輸出檔名與輸入相同、副檔名改為 .pdf
# 用法: scripts/md2pdf.sh rp/Q2_rp.md
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "用法: $0 <input.md> [output.pdf]"
  exit 1
fi

INPUT="$1"
OUTPUT="${2:-${INPUT%.md}.pdf}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TITLE="$(basename "${INPUT%.md}")"
TMP_HTML="$(mktemp -t md2pdf).html"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

pandoc "$INPUT" -o "$TMP_HTML" --standalone --metadata title="$TITLE" -c "$SCRIPT_DIR/md2pdf.css"
"$CHROME" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$OUTPUT" "file://$TMP_HTML"
rm -f "$TMP_HTML"

echo "已產生: $OUTPUT"
