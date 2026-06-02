# Corpus Policy

## Role
- `cheap_corpus.md` 是純文字語料，不是原始畫面還原檔。
- 它只保存對抽取有用的內文內容，不保存 UI、排版裝飾或來源 metadata。

## Format
- 每篇固定格式：
  - 四位數編號一行
  - 空行
  - 貼文正文
- 不使用 markdown 標題。
- 不使用 `【...】` 當小標格式。
- 不使用 HTML 標籤。

## Cleanliness Rules
- 不保留刪除線表示法：
  - `~~...~~`
  - `<del>...</del>`
  - `<s>...</s>`
- 不保留來源畫面的視覺刪除線語意。
- 若原圖有大字、小字、字重差異，進 corpus 時一律壓成普通內文。
- 若原文有語氣符號或促銷口吻，保留內容，但不要保留會被 parser 誤判成格式的記號。

## Scope
- 只留對 Cheap 寫作有用的內容。
- 無意義 placeholder、OCR 雜訊、空殼貼文應移除。
- 篇號重排後，後續 artifacts 必須同步重建。
