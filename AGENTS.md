# 專案協作規範

## 專案資訊

- 專案名稱：和北極星境遇
- 專案目的：整理學習共同體哲學資料與粉絲頁 Logo / 品牌素材，支援後續公開分享、貼文、簡報或網站製作。
- 工作目錄：`G:\我的雲端硬碟\和北極星境遇`
- Repository URL：https://github.com/hsuyiping-rgb/hebeijixing-jingyu（私有）
- 預設分支：`main`

## Obsidian

- Vault：`G:\我的雲端硬碟\secondbrain`
- 專案儀表板：`平平校長的AI學習作品/和北極星境遇.md`
- 穩定規範放在本檔；進度、待辦與阻礙放在 Obsidian 儀表板。

## 工作區角色

- 本工作區保存可交付素材、專案文件與後續程式碼。
- Obsidian 保存專案狀態與工作紀錄，不存放主要產出原始碼。
- GitHub 已連接；提交、推送前仍需先確認範圍。
- 課例分析子專案（`學習共同體課堂影片分析/<課例名>/`）各自有 `handoff.md` 作為跨 session 交接檔，收工時必寫。
- 大型媒體（`*.mp4`／`*.mp3`／`*.m4a`／`*.wav`）已由根目錄 `.gitignore` 排除，勿 git add。

## 巢狀 repo（勿 git add）

工作目錄底下有兩個路徑是**各自獨立的 git repo**，有自己的 GitHub 遠端與備份，不屬於本 repo 的素材：

| 路徑 | 自己的遠端 |
|------|-----------|
| `學習共同體課堂影片分析/宇津睦台小學/` | `slc-mochimochi-lesson-study` |
| `課堂檔案/2026 日本 SLC 國中生物：未知動物 A／鴨嘴獸探究/` | `2026-japan-slc-presentation` |
| `學習共同體哲學實踐教師素養/` | `slc-philosophy-teacher-literacy` |

對它們執行 `git add` 會產生壞掉的 gitlink：外層只記一個 commit SHA、不含檔案內容，clone 後拿到空資料夾且無從取得。要更新請 `cd` 進去各自 commit / push。兩者已加入根目錄 `.gitignore`，`git status` 不再列出，不必再逐次判斷。

## 開工規則

使用者說「開工」「我來了」「上次做到哪」時：

1. 使用全域 `startup` 技能。
2. 讀取本檔與 Obsidian 儀表板。
3. 檢查 Git 狀態與目前檔案。
4. 回報目前狀態、下一步與阻礙。

## 收工規則

使用者說「收工」「下班」「結束」時：

1. 使用全域 `shutdown` 技能。
2. 更新 Obsidian 儀表板的最近變更與下一步。
3. 檢查 Git 狀態與差異。
4. 只有在使用者明確授權時才 commit / push。

## 命令

目前尚未設定開發、測試、建置或部署命令。

## Google Drive 上的 Git 注意事項

本 repo 位於 Google Drive 同步資料夾，git 寫入偶爾會撞到鎖檔：

```
error: Unable to create '.../.git/packed-refs.lock': File exists.
```

**這不一定代表操作失敗**。2026-07-25 遇到時 push 其實已成功（`git ls-remote origin main` 與本地 HEAD 一致），只有更新 `packed-refs` 這個本機簿記步驟失敗。處理順序：

1. 先用 `git ls-remote origin <branch>` 比對本地 `git rev-parse <branch>`，確認遠端到底有沒有收到
2. 用 `Get-Process git` 確認沒有 git 程序還在跑
3. 才刪除殘留的 0 bytes 鎖檔，並設 `git config windows.appendAtomically false` 降低復發

不要一看到錯誤就重跑 push 或 reset——先確認遠端實際狀態。

## 安全規則

- 不提交 `.env`、API key、token、cookie、credentials、secrets 或任何私密設定。
- 不提交 `.codex/`、`.claude/` 等本機代理資料夾。
- 若未來包含學生或個資，使用班級代碼、座號或匿名代稱，不使用真實姓名。
- 不覆蓋既有素材；需要新版時以版本化檔名保存。
