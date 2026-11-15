# 王斐瑜 504 數學公開課課例分析交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。詳細決策與踩坑寫在 Obsidian 儀表板 `平平校長的AI學習作品/和北極星境遇.md`。

## 專案基本資訊
- 授課：王斐瑜老師｜504｜2026-10-15｜翰林五上數學 第五單元「立體形體」
  - 前段 00:00–14:10：5-1 面的垂直與平行（p.67 練習、p.68–69）
  - 後段 14:10–39:35：5-2 柱體和錐體的分類（p.70，附件 21–32）
- 影片：https://youtu.be/a_6dfDljGCY（單機位 39:35）
- 決定：簡報 learning 風格、不接 NotebookLM、不加水彩插圖

## ⏯️ 目前做到哪（2026-11-15）
2026-10-16 已完成：字幕三源校正、`output/analysis.txt`（17 段＋理答六策略）、Word v1–v3、三版簡報、`簡報/web/`（未發布）。

2026-11-15 新增（都是另存新檔，沒有覆蓋舊檔）：
1. 《教師花傳書》p.44–62 × 本課例對照：
   - `花傳書p44-62×504課例_概念對照與討論問題_v2_呼應張力詳述.md/.docx`（**最新**，第一版已不在本機：13 個概念的「呼應或張力」欄詳寫，附頁碼、時間碼、師生原話；15 題討論問題、★ 優先三題、主持流程）
2. 圖解 `output/圖解/課堂流程圖.png`、`理答策略統計.png`（1360px 寬，無學生影像）
3. Word `output/課例分析_…_v4_含圖解.docx`：v3 內容＋卷首兩張圖解
4. 簡報 `簡報/slides_含截圖與影片_720p_v2_含圖解與花傳書.pptx/.html`：**最新版**，74 頁、175MB
   - 圖解總覽 2 頁；每段詮釋頁右上標出對應的花傳書概念；花傳書摘要＋13 個概念頁＋討論問題 6 頁＋主持流程
   - 舊版最後的理答長條圖已改用圖解二

## 🚦 目前狀態
- ❗ 舊版檔案在本機不見了，不是本次 Agent 刪的（11:28 還讀得到 v3），看起來像是清掉舊版、只留最新版：
  - `output/` 的 Word v1、v2、v3（`git status` 顯示 D）：仍在 commit 7a0a3a2，可以 `git restore` 救回
  - 花傳書對照第一版 md/docx：從沒進 git，只能從 Google 雲端硬碟垃圾桶找
  - **等使用者確認是否刻意刪除**
- 720p 兩版簡報都還沒在 PowerPoint 實際點開影片播放過
- HTML 發布含學生影像的版本仍待使用者決定（同 10-16 狀態）

## ➡️ 下一步
1. 處理 Word v1–v3 不見的問題（救回或確認刪除）
2. 議課前在 PowerPoint 打開 `…_720p_v2_含圖解與花傳書.pptx`，抽幾支影片試播
3. 第 11、15 段是否為教師代答、「互相平行」由誰說出，議課時請授課者或觀課者確認，回填 analysis.txt 後重建

## 🔁 重建指令（在本資料夾執行）
- 字幕：改 `output/corrections.json` → `python -X utf8 -I build_final.py output`
- Word：`python -X utf8 -I build_docx.py . <檔名.docx>`（v4 卷首圖解是另外插入的，重建 Word 不會自動帶圖）
- 20 頁簡報：`python -X utf8 -I build_slides.py . [檔名.pptx]`（內容在 `簡報/slides_content.json`）
- 截圖＋影片簡報（舊版）：`python -X utf8 -I build_slides_media.py . slides_含截圖與影片_720p.pptx _720`
- **含圖解＋花傳書版**：`python -X utf8 -I build_slides_media_v2.py . slides_含截圖與影片_720p_v2_含圖解與花傳書.pptx _720`
  - 花傳書內容直接讀 `花傳書…_v2_呼應張力詳述.md`（改 md 就能更新）；各段對應概念寫在腳本的 `SEC_CONCEPTS`
- 圖解 PNG：本次以 headless Chrome 截 HTML 產生，HTML 原檔在暫存區沒有保留；要改圖得重做

## ⚠️ 注意事項
- 花傳書原檔在 `教師花傳書/`（獨立巢狀 repo，勿從外層 git add）；van Hiele 層次是補充觀點，非花傳書原文，文件中已註明
- headless Edge 截圖在這台電腦沒產出檔案；改用 Chrome 並加 `--user-data-dir` 才成功
- 720p 只有畫面（`output/video_720_noaudio.mp4`）；聲音用 `audio_boost.mp3`。yt-dlp 須 2026.08.19 以上
- 各組發表（25:15–28:00）學生原音辨識不出，第 10–12 段只能依教師轉述與板書
- 含學生影像或姓名的檔案都已 gitignore（截圖、片段、媒體版簡報含 v2、web/、未校正字幕、教材 PDF）
- 語音分辨不出他／她，文字一律用「他」
- `.git/packed-refs.lock`（0 bytes，9/24）仍在；收工時仍有 git.exe 在跑，所以沒刪

## 🕐 最後更新
2026-11-15｜Claude Opus 5.5 @ DESKTOP-31QBU95｜Git push：待推
