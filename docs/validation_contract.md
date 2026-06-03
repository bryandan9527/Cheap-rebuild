# Cheap Validation Contract

## Goal
- 檢查 corpus、extraction、writing、draft 四層是否都還對。

## Corpus Checks
- source 只允許純文字內容
- 不允許 markdown 標題
- 不允許刪除線標記
- `entry_id` 必須能由 `clipNNN.md` 穩定推導

## Extraction Checks
- 高信心樣本都要有：
  - `reasoning_pattern`
  - `primary_route`
  - `topic_tags`
  - `angle_statement`
  - `cheap_push_moves`
- records 必須能追溯到 `source_path`

## Writing Checks
- 任一事件都要能收斂到單一 `Reasoning`
- 任一事件都要能收斂到單一 `Route`
- `Topic` 可以多選，但不能回頭搶主腦位置

## Draft Checks
- 有明確角度句
- 有主 `Reasoning`
- 有主 `Route`
- 至少一種 cheap 推進方式
- 收尾不是中性總結
- 不能只是重述新聞
- 不能只有立場沒有推進
