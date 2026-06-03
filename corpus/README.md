# Cheap Corpus

`corpus/` 是 Cheap 語料的主目錄，分成兩層：

- `source/`
  - 唯一人工維護入口
  - 每篇語料一檔，檔名固定為 `clipNNN.md`
- `derived/`
  - 由 `source/` 自動重建的衍生輸出
  - 給 extraction、analysis、writing 驗證流程使用

## Standard Flow
1. 查看 `corpus/source/` 目前最大 `clip` 編號
2. 建立下一號 `clipNNN.md`
3. 將單篇純文字語料存入該檔
4. 執行 `python3 scripts/build_cheap_artifacts.py`
5. 讓系統自動重建 `corpus/derived/` 內全部衍生檔
6. 需要驗證時，再執行 `python3 scripts/validate_cheap_artifacts.py`

## Rules
- 新篇只新增到 `corpus/source/`
- 不可直接修改 `corpus/derived/`
- source 只保留對 Cheap 有用的純文字內容，不保留 UI 還原或畫面 metadata
