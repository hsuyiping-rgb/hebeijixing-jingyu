# 交接檔 handoff — SLC-尋找的人

## ⏯️ 目前做到哪
把《尋找的人》課例研究簡報（`output/slides.html`，20 張投影片）發布上線，並整理進校長個人網頁。

## 🚦 目前狀態
- ✅ **Firebase 部署**：簡報已上線 → https://tazunebito-lesson.web.app （站台 `tazunebito-lesson`，slc-die-mode 專案）。
  - 原本先部署到 `gongitsune-lesson`，因站名與內容不符，已改名：建 `tazunebito-lesson` → 部署 → **刪除舊站 `gongitsune-lesson`**。
  - 部署用資料夾：`output/firebase_tazunebito/`（index.html + images/，48MB）。**不進 git**——內容是 `slides.html` 與 `images/` 的複本，隨時可重建。
    - ⚠️ 2026-07-25 更正：先前這裡誤記為「已加進根 .gitignore，不進 git」。實際上規則是在檔案**已被追蹤之後**才加的，而 **gitignore 對已追蹤檔案完全無效**，所以那 23 個檔（48MB）一直都在版控裡，還與 `output/images/` 內容重複。已用 `git rm -r --cached` 移出版控（磁碟檔案與線上站台皆未受影響），規則現在才真正生效。
  - 重新部署指令：`cd output/firebase_tazunebito && firebase deploy --only hosting:tazunebito-lesson --project slc-die-mode`
- ⚠️ **校長個人網頁卡片（尚未上線）**：`G:/我的雲端硬碟/kfes/校長個人網頁/classroom-observation.html` 的《尋找的人》卡片已改：
  - 縮圖換成第一張投影片（縮 900px 存回 `assets/slc-tazunebito-thumb.png`）
  - 連結改指向搬入的 `slc-tazunebito-slides/slides.html`（簡報＋20 圖已複製進該站專案）
  - **此站部署在 Firebase `teaching-3b748`，本次只改了本機檔案、尚未 deploy 上線。**
  - 注意：`kfes/校長個人網頁` 不是 git repo（只有 AGENTS.md），這些改動沒有版本備份。

## ➡️ 下一步
1. 若要讓校長網頁卡片上線 → 到 `teaching-3b748` 專案部署 `kfes/校長個人網頁`（需先確認該站的 firebase 設定與 target）。這是本課例唯一未完成的項目。
2. ~~決定 288 個「已刪除仍追蹤」的舊課堂檔要不要清掉~~ → **已解決**，2026-07-25 查證 `git ls-files -d` 為 0。

## ⚠️ 注意事項
- Firebase 站台 ID 無法改名，只能「建新站→部署→刪舊站」，網址會跟著換。
- 部署用 `output/firebase_*/` 內獨立 firebase.json（用 `"site"` 直接指定站台），不動根目錄共用設定，確保只部署目標站、不影響其他站。
- **gitignore 不會讓已追蹤的檔案脫離版控**。加規則前先用 `git ls-files <path>` 確認是否已在版控裡；已追蹤的要另外 `git rm -r --cached`，否則會以為擋住了、其實一直在推。
- 已查證仍為真（2026-07-25）：https://tazunebito-lesson.web.app 回 200、舊站 `gongitsune-lesson` 回 404 確實已刪。

## 🕐 最後更新
2026-07-25 · Claude @ DESKTOP-31QBU95 · Git push：{{PUSH_STATUS}}
