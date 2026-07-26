# 學習共同體課堂影片分析／濱之鄉脇坂圭吾水庫（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
進行日本濱之鄉小學脇坂圭吾老師「宮瀨水庫」社會課課例研究與簡報/文案產製，並部署線上網站。

## 關鍵時程
<!-- 格式：- 事件名稱：日期（說明）；沒有就留白 -->
- 目前暫無特定關鍵時程。

## 目標與路線圖
- [x] 階段一：影片下載、ASR 語音轉譯、SRT 校對與逐字稿產出
- [x] 階段二：課例分析報告（描述-詮釋-反思）與扣連學共概念
- [x] 階段三：代表性影格擷取（20張）與 AI 繪製插圖（21張）
- [x] 階段四：自動生成 PPTX/HTML 簡報與 Firebase 線上部署 (https://miyagase-lesson.web.app)
- [x] 階段五：補上第 21 張的 screenshots (05:29 影格) 與更新 `screenshots_review.html`（待人工複查最新 21 張插圖內容）

## 資料夾結構
```
├── handoff.md                        # 交接檔，記錄目前狀態與下一步
├── agents.md                         # 本專案藍圖 (AGENTS.md)
└── output/                           # 專案產出與媒體檔 (大型媒體已 gitignore)
    ├── analysis.txt                  # 課例研究分析報告
    ├── audio.mp3                     # 擷取的課堂影片音訊檔 (已 gitignore)
    ├── audio_groq.json               # Groq Whisper 轉譯之 Word-level JSON (已 gitignore)
    ├── concept.txt / concept.png     # 1080×1080 社群概念圖
    ├── firebase_miyagase/            # Firebase 部署目錄
    ├── illustration_mapping.md       # 21 章節插圖對照表
    ├── images/                       # 21 張 AI 重繪插圖 (JPEG q90)
    ├── images_original/              # 21 張 AI 重繪原始圖 (PNG, 已 gitignore)
    ├── images_review_all_21.jpg      # 人工複查用拼貼圖
    ├── screenshots/                  # 觀課原始截圖 (目前 20 張)
    ├── screenshots_review.html       # 擷圖確認網頁 (含時間碼與對應概念)
    ├── slides.html                   # 網頁版簡報檔
    ├── slides.pptx                   # 生成的可編輯 PPTX 簡報檔
    ├── subtitles.srt                 # 校對後的 SRT 字幕檔
    ├── transcript.txt                # 原始逐字稿
    ├── transcript_from_srt.txt       # 字幕逐字稿
    ├── validate_illustrations.py     # 插圖比例與完整性驗證腳本
    ├── video.mp4 / video.f137.mp4    # 原始影片檔 (已 gitignore)
    └── 新媒體文案包_宮瀨水庫價值思辨_20260726/ # FB/IG/Reels 社群貼文文案包
```

## 同步層級（本專案初始化至第 L2 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | `hsuyiping-rgb/hebeijixing-jingyu` (私有 repo) | 指定時 |
| L3 | Obsidian | GDrive Vault `secondbrain` 中的專案儀表板（未於本機開啟 MCP） | 有需要時 |

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- 大型媒體（`*.mp4`／`*.mp3`／`*.m4a`／`*.wav`）已排除，切勿 `git add`
