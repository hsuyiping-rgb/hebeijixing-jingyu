# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian。

## ⏯️ 目前做到哪

技能已實測**五課**（數學、國語、社會各一，自然兩課）。

**2026-09-13 這一天（多輪，皆已推，最後 commit `6da8aa0`）：**

1. **第五課**：南一六上自然〈熱對物質的影響〉活動 1 第 3 節（固體熱脹冷縮），挑戰性課題
   「銅球加熱卡住後改加熱銅環，會過／更卡／一樣？」三派預測上牆 → 兩支蠟燭同時加熱驗證 → 串連追混淆變因。
   時間 9／20／11。產出在 `教案成果/六年級_自然_熱對物質的影響_20260913/`（無圖版進版控，含圖版不進）。
2. **教材首次走出版社平台**：NaniBox3（`box3.nani.com.tw/resource` → 教材資源 → 課習教 PDF → 教師專用課本／習作「單檔下載」，
   按單元拆，課本一單元 ~180 MB、文字層可直接 `fitz` 抽）。Claude in Chrome 要側邊面板開著且同帳號才連得上；
   親師生平台登入由使用者本人完成。教材與 `教材摘要.md` 在 `教材/六年級_自然_熱對物質的影響/`。
3. **技能補強**（真實來源＋`~/.claude` 複本皆已同步）：`教材摘要.md` 成為 Step 1 固定產出（四段格式）；
   候選跨節、型態未說時寫建議並確認；Step 3 加「配比下限」（挑戰性探究 ≥ 20）與「課本沒做過的實驗變體須課前試做」；
   Step 4 加自製學習單圖規則（`附件_學習單_*`，進版控，`--無圖` 改為只略過 `附件_課本*`）；
   新檔 `references/自然領綱代碼.md`（INa-Ⅲ-1～8 已查證）；`科目_自然.md` 加「實驗變體三道檢核」。
4. README／SKILL／欄位對照**移除學校名稱**（依使用者要求）。
5. 多變的天氣 2-2 產出 `教學流程簡報.pptx`（8 頁，pptxgenjs，驗證通過，已進版控）。

## 🚦 目前狀態

- 技能可用。硬檢核 15 條。母 repo 與 `origin/main` 同步（`6da8aa0`）。
- **五課教案都缺 Step 0 欄位**（學校、班級人數、日期節次、教學者、備課成員、特殊學生），文中 `〔待補〕`。
- 熱對物質的影響另有四項待教師確認：節次是否為活動 1 第 3 節、前一節是否已做完 p.49 加熱銅球、
  pe-Ⅲ-2 全文、**銅環同時加熱 3 分鐘是否足夠（推估值，要課前試做）**。
- dotfiles 端（chezmoi）**本次未同步**：`~/.claude/skills/slc-lesson-plan/` 改了 SKILL.md、README.md、
  `references/科目_自然.md`、`references/制式表欄位對照.md`、`scripts/build_docx.py`，新增 `references/自然領綱代碼.md`。

## ➡️ 下一步

1. chezmoi 同步技能複本：既有檔 `chezmoi re-add`，新檔 `chezmoi add ~/.claude/skills/slc-lesson-plan/references/自然領綱代碼.md`，然後 push dotfiles。
2. 等使用者提供 Step 0 資料，補五課基本欄位、觀課焦點指名對象、串連進程的生1／生2／生3，重跑 `build_docx.py`（含圖版與無圖版各一次）。
3. （選做）exam-composer 的 Step A 補一句「南一自然教師專用課本按單元拆」。

## ⚠️ 注意事項

- **`.git/packed-refs.lock` 會反覆殘留在母 repo**（`和北極星境遇/.git/`，疑為 GDrive 同步搶檔）。commit 本身成功；
  下次 git 動作前 `rm -f` 掉即可。
- **母 repo `hebeijixing-jingyu` 是 PUBLIC。** 不進版控：`範本/`、`教材/`、課文附件、`附件_課本*`、`*（含課本圖）.docx`、`tmp/`。
  **自製的 `附件_學習單_*` 要進版控**，命名別用 `附件_課本` 開頭。
- `--無圖` 現在只略過 `附件_課本*`（2026-09-13 起）；自製圖兩版都放。
- **版面字型是新細明體 12pt**，要換改 `build_docx.py` 的 `BODY_FONT`。
- **auto mode 的權限分類器會擋 commit/push**，等使用者說「commit」再動。
- **`範本/公開課教案參考格式.docx` 只在 DESKTOP-31QBU95**，換電腦要手動帶 `範本/`。
- 輸出 docx 被 Word 開著會 `PermissionError`，請使用者關掉再重跑。
- LibreOffice：`"/c/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf`；bash 裡 `soffice` 不在 PATH。
- pptx 產製：pptxgenjs 不在全域，要在 scratchpad `npm install pptxgenjs`；pptx skill 的 `soffice.py` 包裝在這台跑不起來，直接呼叫上面的 exe。
- 技能單一真實來源 `skills/slc-lesson-plan/`，`~/.claude/skills/` 是複本，由 chezmoi 管。
- 制式表三段是**導入與發現／探究與深化／挑戰與聚斂**；`領域課程綱要` 是二維表，斜線表頭不要覆寫。
- 讀寫 docx 一律 `python -X utf8`；改檔與 `git add` 分開下。

## 🕐 最後更新

- 時間：2026-09-13
- 更新者：**Claude Opus 5** @ DESKTOP-31QBU95
- Git push：母 repo 待推（本收工 commit）；dotfiles ❌ 未推（本次未跑 chezmoi，見下一步 1）
