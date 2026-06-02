# Reasoning Features

## Purpose
- 這份文件定義抽取時要抓哪些訊號，才能穩定判斷 reasoning。

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
- `moral_signals`
  - 可悲
  - 離譜
  - 噁
  - 爛

## Resolution Rule
- 若 `plain_language_signals + incentive language` 很強，優先 `誘因白話拆解`
- 若 `cost_signals` 很強，優先 `荒謬成本換算`
- 若 `history_international_signals` 很強，優先 `歷史國際映射`
- 若 `scenario_signals` 很強，優先 `情境推演判斷`
- 若 `risk_reward_signals` 很強，優先 `風險收益審判`
- 若 `counterexample_signals` 很強，優先 `反例打臉`
- 若事件主要是把制度翻成生活場景，優先 `抽象議題翻成生活常識`
- 若篇幅短且情緒先行，才優先 `先定調再追責`
