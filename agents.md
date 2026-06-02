# Cheap Agents

## Purpose
- 這份文件是專案唯一入口。
- 它只負責控制專案進程、資訊分流與驗證順序。
- 內容細節全部下放到 `corpus/`、`extraction/`、`writing/`、`workflows/`、`validation/`。

## Core Objective
- 用 corpus 歸納 Cheap 的通用思考模式與寫作路線。
- 讓新事件輸入後，先選怎麼想，再選怎麼寫，最後再套題材適配。
- 避免系統退化成新聞分類器或新聞摘要器。

## Writing Spine
`Event -> Reasoning -> Route -> Topic -> Draft`

## Layer Meaning
- `Event`
  - 使用者丟進來的事件摘要、原話、數字、反例與限制。
- `Reasoning`
  - 先決定這件事要怎麼想。
  - 例：反例打臉、誘因白話拆解、荒謬成本換算。
- `Route`
  - 再決定文章怎麼鋪。
  - 例：先摘要再翻成白話、先拋說法再反例拆解。
- `Topic`
  - 最後補題材適配。
  - 例：政黨攻防、公共治理、交通治理、設計品牌。
- `Draft`
  - 最終貼文成品。

## Single / Multi Rules
- `Reasoning` 必須單選。
- `Route` 必須單選。
- `Topic` 可以多選。
- 如果事件同時跨 2 到 3 個題材，先維持同一個 `Reasoning` 與 `Route`，再用多個 `Topic` 補材料與禁忌。

## Task Flows
- `research`
  - 文件：[workflows/research.md](/Users/bryandan/Documents/Cheap-rebuild/workflows/research.md)
  - 任務：補事件材料，整理 `EventBrief`
- `extraction`
  - 文件：[workflows/extraction.md](/Users/bryandan/Documents/Cheap-rebuild/workflows/extraction.md)
  - 任務：從 corpus 抽出 reasoning、route、topic 與證據形狀
- `writing`
  - 文件：[workflows/writing.md](/Users/bryandan/Documents/Cheap-rebuild/workflows/writing.md)
  - 任務：從 `EventBrief` 走到 `Draft`
- `validation`
  - 文件：[workflows/validation.md](/Users/bryandan/Documents/Cheap-rebuild/workflows/validation.md)
  - 任務：檢查不是新聞摘要、路線有收斂、抽取有完整性

## File Map
- corpus
  - 語料與語料政策
  - 讀 [cheap_corpus.md](/Users/bryandan/Documents/Cheap-rebuild/corpus/cheap_corpus.md)
  - 讀 [corpus_policy.md](/Users/bryandan/Documents/Cheap-rebuild/corpus/corpus_policy.md)
  - 讀 [corpus_analysis.md](/Users/bryandan/Documents/Cheap-rebuild/corpus/corpus_analysis.md)
- extraction
  - 抽取欄位與 reasoning 特徵
  - 讀 [extraction_spec.md](/Users/bryandan/Documents/Cheap-rebuild/extraction/extraction_spec.md)
  - 讀 [reasoning_features.md](/Users/bryandan/Documents/Cheap-rebuild/extraction/reasoning_features.md)
- writing
  - 產文主系統與寫作知識
  - 讀 [writing_system.md](/Users/bryandan/Documents/Cheap-rebuild/writing/writing_system.md)
  - 讀 [interfaces.json](/Users/bryandan/Documents/Cheap-rebuild/writing/interfaces.json)
  - 讀 [reasoning/index.md](/Users/bryandan/Documents/Cheap-rebuild/writing/reasoning/index.md)
  - 讀 [routes/index.md](/Users/bryandan/Documents/Cheap-rebuild/writing/routes/index.md)
  - 讀 [topics/index.md](/Users/bryandan/Documents/Cheap-rebuild/writing/topics/index.md)
- workflows
  - 任務流程文件
- validation
  - 驗證規則與檢查表

## Non-Skippable Rules
- 不要從 `Event` 直接跳到 `Draft`。
- 不要把 `workflow` 當成內容分流名詞。
- 不要把 `Topic` 當成最高層主腦。
- 只要材料不足以支撐 `Reasoning`，先回 research 補材料，不要硬生成。
- corpus 必須維持純文字，不保留刪除線或 markdown 標題。

## Verification Gates
1. corpus 乾淨
   - 沒有刪除線標記
   - 沒有 markdown 標題
   - 只保留 `編號 + 內文`
2. extraction 完整
   - 高信心樣本都要有 `reasoning_pattern`、`primary_route`、`topic_tags`
3. writing 可收斂
   - 任一事件都能收斂到單一 `Reasoning` 與單一 `Route`
4. draft 不退化
   - 必有 angle
   - 必有 cheap 推進方式
   - 不像新聞摘要
