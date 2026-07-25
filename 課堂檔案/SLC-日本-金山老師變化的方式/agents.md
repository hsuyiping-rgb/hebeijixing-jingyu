# SLC-日本-金山老師變化的方式（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
學習共同體（SLC）日本公開課「金山老師：變化的方式」四年級數學課例分析專案。從課堂影片出發，進行語音轉譯與「描述—詮釋—反思」課例研究，重繪抹茶綠繪本插圖，產出可編輯的 16:9 PPTX 簡報、互動式 HTML 簡報、社群發布包，並部署至 GitHub Pages。

## 關鍵時程
- 課例素材整理：2026-07-12（social-post-kit 圖像提示與發布檢核產生）
- 目前 GitHub Pages 部署 repo：`hsuyiping-rgb/slc-kanayama-lesson-study`

## 目標與路線圖
- [x] 影片語音轉譯與逐字稿（`字幕與逐字稿/`）
- [x] 課例研究分析與抹茶綠插圖重繪（`圖片/`）
- [x] 16:9 可編輯 PPTX 簡報（`簡報/output/`）
- [x] 互動式 HTML 簡報（`HTML簡報/output/`）
- [x] GitHub Pages 部署（`GitHub部署/deploy_github_pages/`）
- [x] 社群發布包（`文字資料/social-post-kit/`）
- [x] Firebase Hosting 多站台部署：新增 `kanayama-henka-lesson` 站（2026-07-24）
- [x] 一頁式響應版 HTML 簡報重建（真 HTML 文字＋SVG 折線圖，取代 WebP 圖片版）
- [ ] 收尾與後續維護（視需求）

## 資料夾結構
<!-- 初始化掃描；新增檔案時更新 -->
- `HTML簡報/` — 互動式 HTML 簡報原始碼與 output（15 檔）
  - `HTML簡報/firebase_kanayama/index.html` — Firebase `kanayama-henka` 站台的正式部署檔（一頁式響應版，2.1MB 自包含）
  - `HTML簡報/_firebase_kanayama_backup/` — 原播放器版備份（不部署）
- `PDF文件/` — 金山老師四年級數學題目 PDF
- `_work/` — 建置腳本與中間素材（6 檔）
- `圖片/` — 抹茶綠插圖、slide 圖、output 圖片（229 檔）
- `字幕與逐字稿/` — 語音轉譯字幕與逐字稿（3 檔）
- `文字資料/` — social-post-kit 社群發布素材（圖像提示、發布檢核等，10 檔）
- `暫存/` — 暫存工作檔（9 檔）
- `簡報/` — 可編輯 PPTX 簡報 output（8 檔，含大檔）
- `聲音與影片/` — 課堂影片與音訊（`output/video.mp4` 等大檔）
- `腳本/` — 處理腳本（4 檔）
- `GitHub部署/deploy_github_pages/` — GitHub Pages 部署 repo（已連 `slc-kanayama-lesson-study`）

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | 沿用部署 repo：https://github.com/hsuyiping-rgb/slc-kanayama-lesson-study （`GitHub部署/deploy_github_pages/`，僅 GitHub Pages 發布用；專案大檔不入版控） | 指定時 |
| L3 | Obsidian | SLC-日本-金山老師變化的方式/專案工作流程.md（vault 內） | 有需要時 |

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- ⚠️ 本專案含 2GB 大型媒體（video.mp4、多個 PPTX），**不整包 push 到 GitHub**；版本控制只納入文字/腳本/HTML 原始碼，大檔以 `.gitignore` 排除
- GitHub Pages 發布走既有的 `GitHub部署/deploy_github_pages/` 子 repo，勿與專案版控 repo 混淆
