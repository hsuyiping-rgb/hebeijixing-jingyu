# 王斐瑜 504 數學公開課課例分析交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。詳細決策與踩坑寫在 Obsidian 儀表板 `平平校長的AI學習作品/和北極星境遇.md`。

## 專案基本資訊
- 授課：王斐瑜老師｜504｜2026-10-15｜翰林五上數學 第五單元「立體形體」
  - 前段 00:00–14:10：5-1 面的垂直與平行（p.67 練習、p.68–69）
  - 後段 14:10–39:35：5-2 柱體和錐體的分類（p.70，附件 21–32）
- 影片：https://youtu.be/a_6dfDljGCY（單機位 39:35）
- 決定：簡報 learning 風格、不接 NotebookLM、不加水彩插圖

## ⏯️ 目前做到哪（2026-10-16）
已完成：
1. 字幕三源校正 → `output/subtitles_final.srt`、`transcript_corrected.md`（含可信度）；燒錄用 `subtitles_burn.srt`（只含已校正語句）
2. 課例分析 `output/analysis.txt`：17 段，描述—詮釋（含「理答：」六策略分析）—反思
3. Word：`output/課例分析_…_v3_含理答策略_板書更正.docx`（最新；v1、v2 保留）
4. 簡報（全部另存，未互相覆蓋）：
   - `簡報/slides.pptx/.html`：20 頁純文字版（舊板書文字）
   - `簡報/slides_含截圖與影片.pptx/.html`：52 頁，360p 截圖＋影片（舊板書文字）
   - `簡報/slides_含截圖與影片_720p.pptx/.html`：**最新版**，52 頁、174MB、16 支 720p 燒字幕影片
5. 網頁發布：已準備 `簡報/web/`（16 支壓縮影片，共 96MB；720p 截圖），**還沒發布**

## 🚦 目前狀態
- 發布 HTML 到 claude.ai 那一步被權限檢查以「個資處理（學生臉部影像）」擋下，等使用者決定：
  ①改發布無學生影像的 20 頁 slides.html，或 ②使用者確認已取得同意後再發布含影像版
- 720p 版簡報還沒在 PowerPoint 實際點開影片播放過

## ➡️ 下一步
1. 等使用者決定發布哪一版（見上）；含影像版：把 `slides_含截圖與影片_720p.html` 轉成發布格式 → `web/index.html`，影片超過 64MB 要分兩次上傳
2. 議課前在 PowerPoint 實際播放 720p 版幾支影片
3. 視需要用最新 analysis.txt 重建 20 頁版與 360p 版簡報（目前還是舊的板書文字）

## 🔁 重建指令（在本資料夾執行）
- 字幕：改 `output/corrections.json` → `python -X utf8 -I build_final.py output`
- Word：`python -X utf8 -I build_docx.py . <檔名.docx>`
- 20 頁簡報：`python -X utf8 -I build_slides.py . [檔名.pptx]`（內容在 `簡報/slides_content.json`）
- 截圖＋影片簡報：`python -X utf8 -I build_slides_media.py . slides_含截圖與影片_720p.pptx _720`（截圖時間與片段在 `簡報/media_plan.json`）

## ⚠️ 注意事項
- 720p 只有畫面（`output/video_720_noaudio.mp4`）；聲音用 `audio_boost.mp3`，兩者逐格比對沒有時間偏移。yt-dlp 必須用 2026.08.19 以上版本，舊版下載到約 10MB 就會 403
- 720p 板書：②圓柱體／角柱體／錐體 ③錐體／圓柱體／長方體／梯形體／正方體 ④三角形…圓形，旁邊加註「（體）」；圈起來的數字是座號
- 各組發表（25:15–28:00）學生原音三源都辨識不出，第 10–12 段只能依教師轉述與板書
- 第 11、15 段是否為教師代答，需對照現場觀課紀錄
- 含學生影像或姓名的檔案都已 gitignore（截圖、片段、媒體版簡報、web/、未校正字幕、教材 PDF）
- 語音分辨不出他／她，文字一律用「他」

## 🕐 最後更新
2026-10-16 17:03｜Claude Opus 5.5 @ DESKTOP-HJA3024｜Git push：待推
