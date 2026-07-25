# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（若有 L3）。

## ⏯️ 目前做到哪
把 `kanayama-henka-lesson` 站的 HTML 簡報從「文字烙進 WebP 圖片」重建為**一頁式響應版**（真 HTML 文字、左文右圖向上對齊、3 張折線圖改成 SVG 且 x 軸橫排），經預覽頻道確認後**已正式部署上線**。

## 🚦 目前狀態
- 正式站已上線：https://kanayama-henka-lesson.web.app （一頁式響應版）
- 其他三站未動：hebeijixing-fire-lesson、mochimochi-lesson、slc-die-mode
- 預覽頻道 `onepage-preview` 仍存在，2026-07-31 到期（可留可刪）
- 正式檔：`HTML簡報/firebase_kanayama/index.html`；原播放器版備份在 `HTML簡報/_firebase_kanayama_backup/`

## ➡️ 下一步
1. 若簡報還要微調：改 `HTML簡報/firebase_kanayama/index.html` 後跑 `firebase deploy --only hosting:kanayama-henka --project slc-die-mode`（重建腳本在 scratchpad `build_v2.py`，可搬進專案 `_work/` 保存）。
2. 視需要刪除到期前的預覽頻道 `onepage-preview`。
3. 外層 repo（root 在 `和北極星境遇`）仍有 288 筆搬移後舊路徑刪除未 commit，屬既有待收尾項。

## ⚠️ 注意事項
- **Firebase 部署設定在外層雲端硬碟根目錄**：`firebase.json`（hosting 為陣列，含 `fire-lesson-analysis`、`kanayama-henka` 兩目標）＋`.firebaserc`。部署務必加 `--only hosting:kanayama-henka`，避免動到其他站。
- 課堂資料被外層 repo `.gitignore`，`firebase_kanayama/` 內容不入 git，只靠 Google 雲端硬碟同步——換電腦前確認同步完成。
- 原 18 頁 WebP 版文字不可選取、x 軸直書烙死；勿再回頭用那版。

## 🕐 最後更新
- 時間：2026-07-24
- 更新者：Claude Code (Opus 4.8) @ DESKTOP-31QBU95
- Git push：✅ 已推（commit 4d73aba，外層 repo hebeijixing-jingyu，僅 firebase.json＋.firebaserc）
