#!/bin/bash
# 把 mm7382.github.io 的內容重新轉成 Markdown 鏡像。
# 用法：bash tools/sync.sh        （只產檔，不 commit）
#       bash tools/sync.sh push   （有變動就 commit 並 push）
set -euo pipefail
cd "$(dirname "$0")/.."
SITE="/Users/michaelchuang/Documents/遊戲/mm7382.github.io"
[ -d "$SITE" ] || { echo "找不到網站目錄：$SITE"; exit 1; }

echo "== 轉換 =="
for f in to_md.py courses.py yijian.py pages.py; do
  printf '  %-12s ' "$f"; python3 "tools/$f" write | tail -1
done
echo "== 重建索引 =="
python3 tools/build_indexes.py

echo "== 同步 llms.txt =="
cp "$SITE/llms.txt" llms.txt

echo "== 變動 =="
git status --short | head -20
n=$(git status --porcelain | wc -l | tr -d ' ')
echo "  共 $n 個檔有變動"

if [ "${1:-}" = "push" ] && [ "$n" -gt 0 ]; then
  git add -A
  git commit -q -m "同步網站內容到鏡像（$(date +%Y-%m-%d)）"
  git push -q
  echo "== 已 push =="
fi
