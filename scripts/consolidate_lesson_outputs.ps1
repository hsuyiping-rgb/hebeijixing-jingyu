$ErrorActionPreference = 'Stop'

$out = Join-Path $PSScriptRoot '..\output'
$out = (Resolve-Path $out).Path
$classes = Join-Path $out '課堂檔案'
$utsugi = Join-Path $classes '宇津木台語文寫作_20141112'
$fire = Join-Path $classes '濱之鄉三年級消防社會課'

function Ensure-StandardFolders([string]$lesson) {
  foreach ($name in @('影音', '簡報', '文字稿', '圖片')) {
    New-Item -ItemType Directory -Force (Join-Path $lesson $name) | Out-Null
  }
}

function Copy-FileSet([string[]]$paths, [string]$destination) {
  New-Item -ItemType Directory -Force $destination | Out-Null
  foreach ($path in $paths) {
    Copy-Item -LiteralPath $path -Destination $destination -Force
  }
}

function Copy-DirectoryContents([string]$source, [string]$destination) {
  New-Item -ItemType Directory -Force $destination | Out-Null
  Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $destination -Recurse -Force
}

Ensure-StandardFolders $utsugi
Ensure-StandardFolders $fire

# Final Utsugi deliverables only: 1080p source, final deck, full transcript set, and visual evidence.
Copy-FileSet @(
  (Join-Path $out '影音\宇津木台語文寫作_20141112\宇津木台語文寫作_完整課堂_1080p.mp4')
) (Join-Path $utsugi '影音')
Copy-FileSet @(
  (Join-Path $out '簡報\宇津木台語文寫作_20141112_課例分析_可編輯.pptx'),
  (Join-Path $out '簡報\宇津木台語文寫作_20141112_課例分析.html')
) (Join-Path $utsugi '簡報')
Copy-FileSet @(
  (Join-Path $out '文字稿\宇津木台語文寫作_20141112_NotebookLM_觀議課框架原文.txt'),
  (Join-Path $out '文字稿\宇津木台語文寫作_20141112_NotebookLM架構.json'),
  (Join-Path $out '文字稿\宇津木台語文寫作_20141112_完整課堂.srt'),
  (Join-Path $out '文字稿\宇津木台語文寫作_20141112_完整課堂_逐字稿.txt'),
  (Join-Path $out '文字稿\宇津木台語文寫作_20141112_課例分析.md'),
  (Join-Path $out '文字稿\宇津木台語文寫作_20141112_簡報大綱.md')
) (Join-Path $utsugi '文字稿')
Copy-DirectoryContents (Join-Path $out '圖片\宇津木台語文寫作_20141112_GPT插圖') (Join-Path $utsugi '圖片\GPT插圖')
Copy-DirectoryContents (Join-Path $out '圖片\宇津木台語文寫作_20141112_簡報截圖') (Join-Path $utsugi '圖片\簡報截圖')
Copy-DirectoryContents (Join-Path $out '圖片\宇津木台語文寫作_20141112_觀課截圖') (Join-Path $utsugi '圖片\觀課截圖')
Copy-DirectoryContents (Join-Path $out '圖片\宇津木台語文寫作_20141112_簡報匯出') (Join-Path $utsugi '圖片\簡報匯出')
Copy-FileSet @((Join-Path $out '圖片\宇津木台語文寫作_20141112_簡報匯出_總覽.png')) (Join-Path $utsugi '圖片')

# Final Fire lesson deliverables, including the Firebase entry page and social-media package.
Copy-FileSet @(
  (Join-Path $out '影音\video.mp4'),
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\reels_消防課地域公共性_直式.mp4')
) (Join-Path $fire '影音')
Copy-FileSet @(
  (Join-Path $out '簡報\hamanosato_fire_lesson_analysis_editable.pptx')
) (Join-Path $fire '簡報')
Copy-Item -LiteralPath (Join-Path $out '網站\消防課公開課簡報\index.html') -Destination (Join-Path $fire '簡報\index.html') -Force
Copy-FileSet @(
  (Join-Path $out '文字稿\DELIVERABLES.md'),
  (Join-Path $out '文字稿\lesson_analysis.md'),
  (Join-Path $out '文字稿\subtitles.srt'),
  (Join-Path $out '文字稿\timeline_chunks.txt'),
  (Join-Path $out '文字稿\transcript.json'),
  (Join-Path $out '文字稿\transcript.txt')
) (Join-Path $fire '文字稿')
Copy-DirectoryContents (Join-Path $out '圖片\GPT插圖') (Join-Path $fire '圖片\GPT插圖')
Copy-DirectoryContents (Join-Path $out '圖片\投影片圖片') (Join-Path $fire '圖片\投影片圖片')
Copy-DirectoryContents (Join-Path $out '圖片\關鍵畫面') (Join-Path $fire '圖片\關鍵畫面')
Copy-FileSet @((Join-Path $out '圖片\contact_sheet.jpg')) (Join-Path $fire '圖片')
Copy-DirectoryContents (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\圖片_4比5輪播') (Join-Path $fire '圖片\新媒體發布\輪播')
Copy-DirectoryContents (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\圖片_Reels直式字卡') (Join-Path $fire '圖片\新媒體發布\Reels字卡')
Copy-FileSet @(
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\Reels封面_1080x1920.png')
) (Join-Path $fire '圖片\新媒體發布')
Copy-FileSet @(
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\FB.txt'),
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\IG.txt'),
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\Reels腳本.txt'),
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\Reels說明.txt'),
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\發布清單.md'),
  (Join-Path $out '新媒體\貼文包_消防課地域公共性_20260716\網址與素材說明.md')
) (Join-Path $fire '文字稿\新媒體發布')

$required = @(
  (Join-Path $utsugi '影音\宇津木台語文寫作_完整課堂_1080p.mp4'),
  (Join-Path $utsugi '簡報\宇津木台語文寫作_20141112_課例分析_可編輯.pptx'),
  (Join-Path $utsugi '簡報\宇津木台語文寫作_20141112_課例分析.html'),
  (Join-Path $fire '影音\video.mp4'),
  (Join-Path $fire '簡報\hamanosato_fire_lesson_analysis_editable.pptx'),
  (Join-Path $fire '簡報\index.html')
)
foreach ($path in $required) {
  if (-not (Test-Path -LiteralPath $path)) { throw "Missing staged deliverable: $path" }
}

# User requested removal of old and duplicate output versions after verification.
foreach ($obsolete in @('影音', '簡報', '文字稿', '圖片', '新媒體', '網站')) {
  $path = Join-Path $out $obsolete
  if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force }
}

Get-ChildItem -LiteralPath $classes -Recurse -File | ForEach-Object {
  [PSCustomObject]@{
    Path = $_.FullName.Substring($out.Length + 1)
    SizeMB = [math]::Round($_.Length / 1MB, 2)
  }
} | Sort-Object Path

