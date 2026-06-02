# Extraction Spec

## Goal
- extraction 的任務不是做漂亮分類，而是把 corpus 變成 reasoning-first 系統可直接使用的訊號。

## Required Fields
- `entry_id`
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

## Field Roles
- `reasoning_pattern`
  - 給 writing system 決定這篇主要怎麼想
- `primary_route`
  - 給 writing system 決定最後怎麼鋪文
- `topic_tags[]`
  - 給 topic adaptation 補題材材料與禁忌
- `angle_statement`
  - 確保不是摘要，而是有明確出手角度
- `argument_moves[]`
  - 記錄整篇用了哪些論證動作
- `cheap_push_moves[]`
  - 記錄 Cheap 典型推進方式
- `required_evidence_types[]`
  - 告訴 research 後續需要補什麼材料
- `hook_type`
  - 告訴 writing 開場是數字、問題、說法還是角度句
- `claim_target`
  - 幫助決定貼文攻擊或解構的對象
- `evidence_shape[]`
  - 告訴 route 目前可用的是數字、反例、外部案例還是生活場景

## Extraction Principles
- 先判斷 `Reasoning`，再判斷 `Route`。
- `Topic` 是輕量多標籤，不是第一層分類。
- 同一篇只能有一個主 `Reasoning`、一個主 `Route`。
- 如果一篇文同時碰政治、設計、治理，允許多個 `Topic`，但不能多個主 reasoning。
