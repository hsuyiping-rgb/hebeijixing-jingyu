# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian。

## ⏯️ 目前做到哪

`slc-lesson-plan` 技能建置完成並通過專案初始化。經一輪 grilling 訪談定案全部規格，
建出 SKILL.md（202 行）＋ 7 份 references ＋ 2 份 templates，四科指引都有實例支撐。
已複製到 `~/.claude/skills/slc-lesson-plan/`，本 session 確認技能可被觸發。

## 🚦 目前狀態

- 技能**已實測完成**：2026-09-09 走完 Step 0 → Step 1 → Step 2 → Step 3 → Step 4，
  產出五上數學〈折線圖〉第 4 節公開課教案（`教案成果/五年級_數學_折線圖_20260909/`），
  硬檢核全數通過。教材來自 NotebookLM 筆記本 `3c7df9ba`（翰林五上數學命題成果，含課本全文與教師手冊）。
- Step 4 **已實作**：`scripts/build_docx.py`，吃 JSON 產 docx，並附 `--inspect` 可檢視範本表格幾何。
  通用化後的輸出與原本硬編版逐行比對差異為 0。
- 母 repo 有一個本機 commit，**未 push**。（原先三個 commit 含 `範本/`，已重做為單一乾淨 commit。）

## ➡️ 下一步

1. **實測一課**：挑一個單元走完三階段，特別驗證「10 分鐘內進小組」與 Step 3 硬檢核是否真的擋得住。
2. 寫 Step 4 的 docx 轉檔腳本。
3. 補國內社會科制式表格式的教案實例，回頭校準 `references/科目_社會.md`。

## ⚠️ 注意事項

- **母 repo `hebeijixing-jingyu` 是 PUBLIC。** 本資料夾隨它一起版控，但 **`範本/` 已排除**——
  數學科教案內含 307 班座位表（24 位學生姓名與座號），不可公開。
  `教材/`、`教案成果/` 目前**未**排除：放含學生姓名或照片的檔案進去前要先想清楚，
  必要時比照 `範本/` 加進母 repo 的 `.gitignore`。
- 制式表的三段流程是**導入與發現／探究與深化／挑戰與聚斂**。
  「伸展跳躍」是描述課題難度的詞，**不是流程名**，別寫錯。
- `範本/宇津木台…教案1.pdf` 與 `…2.pdf` 是**同一份指導案的第 1、2 頁**（不是兩份教案），
  且為掃描影像無文字層，要用視覺讀取（`fitz` 轉 PNG 後讀圖）。
- `.git/packed-refs.lock` 曾殘留一個 9/6 的空鎖檔，已於本 session 刪除。若再出現同樣警告，同樣處理。
- 讀寫 docx 時務必用 `python -X utf8`，否則中文會變亂碼——第一次就因此把三段流程名誤讀成
  「伸展與跳躍／挑戰與延伸」，還寫進訪談摘要給使用者看了。
- **範本 `領域課程綱要` 第 2 列的第 2、3 欄是合併儲存格**（整列只有 2 個實際格）。
  分別寫入會後者蓋掉前者，而且 python-docx 讀回來時兩欄看起來都有內容（同一格被讀兩次），
  很容易誤判成功。`build_docx.py` 已用 `Filler.distinct()` 自動處理。
  **改版或換範本前先跑 `build_docx.py --inspect`**，它會標出哪幾列有合併。
- **shell heredoc 寫長 python 腳本會被截斷**。用 `python -X utf8 - <<'PY'` 塞入數百行時，
  bash 報 "here-document delimited by end-of-file"，python 收到半截腳本而語法錯誤。
  長腳本改用 Write 工具寫成檔案再執行。
- **Git Bash 的 `/tmp` 對 Windows 原生 python 不可見**。跨 bash／python 傳檔要用完整 Windows 路徑。
- **改檔與 `git add` 不要寫在同一個指令裡**。曾發生 python 改完檔、同一行接 `git add` 卻只加到
  改動前的內容，導致三個檔案的編輯漏進 commit（事後以 `ec686de` 補上）。
  提交前先看 `git diff --cached` 確認改動真的在裡面。

## 🕐 最後更新

- 時間：2026-09-09
- 更新者：Claude Opus 5 @ DESKTOP-31QBU95
- Git push：❌ 未推（兩個本機 commit 待使用者決定何時 push 到公開 repo）
