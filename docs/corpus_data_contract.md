# Cheap Corpus Data Contract

## Directory Boundaries
- `corpus/source/`
  - 唯一人工維護入口
  - 每篇語料一檔
  - 檔名固定為 `clipNNN.md`
- `corpus/derived/`
  - 由 `corpus/source/` 自動重建的衍生輸出
  - 包含 merged、records、taxonomy、summary、analysis
  - 不可視為第二份 source

## Corpus Format
- source 只保存對抽取有用的純文字內容
- 不使用 markdown 標題
- 不使用 `【...】` 當小標格式
- 不使用 HTML 標籤
- 不保留刪除線表示法：
  - `~~...~~`
  - `<del>...</del>`
  - `<s>...</s>`

## Ingest Flow
1. 查看 `corpus/source/` 目前最大 `clip` 編號
2. 建立下一號 `clipNNN.md`
3. 將單篇原始 corpus 內容壓成純文字後存入該檔
4. 不要同步修改 merged、records 或 `entry_id`
5. 執行 `python3 scripts/build_cheap_artifacts.py`
6. 讓系統自動重建 `corpus/derived/` 內全部衍生檔
7. 需要驗證時，再執行 `python3 scripts/validate_cheap_artifacts.py`

## Entry ID Contract
- `clip001.md` 對應 `entry_id: "0001"`
- `entry_id` 永遠由 source 檔名推導，不由人工指定
