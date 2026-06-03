# Cheap Agents

## Project Goal
- 生成與 Corpus 語料庫相同品質的文章（Corpus-quality）。

## Core Principle
- 先抽取，再生成。
- reasoning-first，不要 topic-first。
- 普遍性優先，避免把單一事件寫成永久規則。
- `Event -> Reasoning -> Route -> Topic -> Draft` 是 Cheap 的生成主幹。
- `corpus/source/clip*.md` 是 source of truth。
- `corpus/derived/*` 是抽取與生成用 derived outputs，不是手工維護入口。

## Two Layers
### Layer 1
- 目的：整理 Cheap 通用能力。
- 內容：
  - 思考模式：讀 [profiles/reasoning_profile.md](/Users/bryandan/Documents/Cheap-rebuild/profiles/reasoning_profile.md)
  - 鋪文路線：讀 [profiles/route_profile.md](/Users/bryandan/Documents/Cheap-rebuild/profiles/route_profile.md)
  - 資料搜集框架：讀 [profiles/research_profile.md](/Users/bryandan/Documents/Cheap-rebuild/profiles/research_profile.md)

### Layer 2
- 目的：依事件題材補材料、語氣與禁忌，不負責主腦判斷。
- 內容：
  - 政黨攻防：讀 [playbooks/partisan_attack.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/partisan_attack.md)
  - 公共治理：讀 [playbooks/public_governance.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/public_governance.md)
  - 交通治理：讀 [playbooks/traffic_governance.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/traffic_governance.md)
  - 設計品牌：讀 [playbooks/design_branding.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/design_branding.md)
  - 國際安全：讀 [playbooks/international_security.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/international_security.md)
  - 科技媒體 AI：讀 [playbooks/tech_media_ai.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/tech_media_ai.md)
  - 生活消費：讀 [playbooks/lifestyle_consumer.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/lifestyle_consumer.md)
  - 歷史反事實：讀 [playbooks/history_counterfactual.md](/Users/bryandan/Documents/Cheap-rebuild/playbooks/history_counterfactual.md)

## Task Flows
- 抽取語料：
  - 讀 [corpus/derived/cheap_taxonomy.json](/Users/bryandan/Documents/Cheap-rebuild/corpus/derived/cheap_taxonomy.json)
  - 讀 [corpus/derived/cheap_corpus_analysis.md](/Users/bryandan/Documents/Cheap-rebuild/corpus/derived/cheap_corpus_analysis.md)
  - 讀 Layer 1 profiles
- 事件判斷：
  - 先讀 Layer 1 profiles
  - 再讀對應 Layer 2 playbook
- 生成文章：
  - `EventBrief -> ReasoningDecision -> RouteDecision -> TopicDecision -> Draft`
  - 不要從 brief 直接跳到 final draft
- 系統文件：
  - 架構：讀 [docs/architecture.md](/Users/bryandan/Documents/Cheap-rebuild/docs/architecture.md)
  - 抽取流程：讀 [docs/extraction_first_workflow.md](/Users/bryandan/Documents/Cheap-rebuild/docs/extraction_first_workflow.md)
  - 介面契約：讀 [docs/writing_interfaces.md](/Users/bryandan/Documents/Cheap-rebuild/docs/writing_interfaces.md)
  - 驗證契約：讀 [docs/validation_contract.md](/Users/bryandan/Documents/Cheap-rebuild/docs/validation_contract.md)

## Decision Contract
- 單篇只允許：
  - 1 個主 `reasoning_pattern`
  - 1 個主 `primary_route`
  - 1 組主 `Topic` 適配方向
- `topic_tags` 可以多選，但只能做 supporting adaptation，不可回頭搶主腦位置。
- 生成優先順序：
  1. 主 `Reasoning`
  2. 主 `Route`
  3. `Topic` playbooks
  4. angle / closing calibration
- 只要材料不足以支撐主 `Reasoning`，先回 research 補材料，不要硬生成。

## Artifact Commands
```bash
python3 scripts/build_cheap_artifacts.py
python3 scripts/validate_cheap_artifacts.py
```
