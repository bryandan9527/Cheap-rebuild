# Cheap Extraction-First Workflow

## Goal
- extraction 的任務不是做漂亮分類，而是把 corpus 變成 reasoning-first 系統可直接使用的訊號。

## Phase Order
1. normalize corpus source
2. build merged corpus artifact
3. extract record-level features
4. assign `reasoning_pattern`
5. assign `primary_route`
6. add `topic_tags`
7. add argument, evidence, hook, opening, closing fields
8. inspect distribution and validate

## Required Fields
- `entry_id`
- `source_path`
- `clean_text`
- `char_count`
- `topic_cluster_id`
- `reasoning_pattern`
- `primary_route`
- `topic_tags[]`
- `angle_statement`
- `argument_moves[]`
- `cheap_push_moves[]`
- `required_evidence_types[]`
- `hook_type`
- `claim_target`
- `evidence_shape[]`
- `opening_move`
- `rhythm_pattern`
- `closing_style`

## Extraction Principles
- 先判斷 `Reasoning`，再判斷 `Route`
- `Topic` 是輕量多標籤，不是第一層分類
- 同一篇只能有一個主 `Reasoning`、一個主 `Route`
- 如果一篇文同時碰政治、設計、治理，允許多個 `Topic`，但不能多個主 reasoning

## Feature Groups
- `counterexample_signals`
  - 反觀
  - 先不說
  - 還有同樣案例
  - 拿別的品牌、國家、制度來對照
- `plain_language_signals`
  - 翻成白話
  - 簡單說
  - 意思是
  - 所以邏輯是
- `cost_signals`
  - 數字密度高
  - 出現金額、工時、流程、費用、薪資
- `history_international_signals`
  - 日本、美國、德國、越南、韓國
  - 歷史上、正史、二戰
- `scenario_signals`
  - 如果
  - 版本一 / 版本二
  - 高機率
  - 會怎樣
- `risk_reward_signals`
  - 風險
  - 收益
  - 代價
  - 值不值得
- `plain_common_sense_signals`
  - 把制度判斷翻成一般人的風險常識
  - 把個案荒謬推進成公信力受損

## Validation Standard
- merged corpus 篇數必須和 source 一致
- 每篇都要保有穩定 `entry_id`
- records 必須能追溯回 `source_path`
- `reasoning_pattern`、`primary_route`、`topic_tags` 必須完整
- route 的 `must_include_moves` 必須真的包含 cheap 推進方式
