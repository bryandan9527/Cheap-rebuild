# Extraction Workflow

## Goal
- 從 corpus 抽出 reasoning-first 系統需要的最小訊號。

## Steps
1. 解析 `cheap_corpus.md`
2. 清理文字與格式
3. 判斷 `reasoning_pattern`
4. 判斷 `primary_route`
5. 補 `topic_tags[]`
6. 補 argument / evidence / hook 欄位
7. 輸出 artifacts

## Verification
- 每篇高信心樣本都要有：
  - `reasoning_pattern`
  - `primary_route`
  - `topic_tags`
  - `angle_statement`
  - `cheap_push_moves`
