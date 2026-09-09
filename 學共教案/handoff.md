# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian。

## ⏯️ 目前做到哪

`slc-lesson-plan` 技能建置完成並通過專案初始化。經一輪 grilling 訪談定案全部規格，
建出 SKILL.md（202 行）＋ 7 份 references ＋ 2 份 templates，四科指引都有實例支撐。
已複製到 `~/.claude/skills/slc-lesson-plan/`，本 session 確認技能可被觸發。

## 🚦 目前狀態

- 技能**可用但未實測**——還沒有真的跑過一次 Step 0 → Step 1 → Step 2。
- Step 4（Markdown 轉 .docx）**尚未實作**，SKILL.md 只寫了方法（python-docx 填 `範本/公開課教案參考格式.docx`），沒有腳本。
- 母 repo 有兩個本機 commit（`fcd3fc8`、`405c0f8`），**未 push**。

## ➡️ 下一步

1. **實測一課**：挑一個單元走完三階段，特別驗證「10 分鐘內進小組」與 Step 3 硬檢核是否真的擋得住。
2. 寫 Step 4 的 docx 轉檔腳本。
3. 補國內社會科制式表格式的教案實例，回頭校準 `references/科目_社會.md`。

## ⚠️ 注意事項

- **母 repo `hebeijixing-jingyu` 是 PUBLIC。** 本資料夾隨它一起版控（使用者已知並選擇此方案），
  `範本/` 內含自強國小教師教案與校長自然科教案，push 後會公開可見。
  放新教材或含學生資料的檔案進 `教材/`、`教案成果/` 前要留意這件事。
- 制式表的三段流程是**導入與發現／探究與深化／挑戰與聚斂**。
  「伸展跳躍」是描述課題難度的詞，**不是流程名**，別寫錯。
- `範本/宇津木台…教案1.pdf` 與 `…2.pdf` 是**同一份指導案的第 1、2 頁**（不是兩份教案），
  且為掃描影像無文字層，要用視覺讀取（`fitz` 轉 PNG 後讀圖）。
- `.git/packed-refs.lock` 曾殘留一個 9/6 的空鎖檔，已於本 session 刪除。若再出現同樣警告，同樣處理。
- 讀 docx 時務必用 `python -X utf8`，否則中文會變亂碼——我第一次就因此誤讀了流程名稱。

## 🕐 最後更新

- 時間：2026-09-09
- 更新者：Claude Opus 5 @ DESKTOP-31QBU95
- Git push：❌ 未推（兩個本機 commit 待使用者決定何時 push 到公開 repo）
