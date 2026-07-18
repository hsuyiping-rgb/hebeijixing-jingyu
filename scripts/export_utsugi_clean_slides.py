from pathlib import Path

import win32com.client


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "課堂檔案" / "宇津木台語文寫作_20141112"
PPTX = OUT / "簡報" / "宇津木台語文寫作_20141112_課例分析_可編輯.pptx"
EXPORTS = OUT / "圖片" / "簡報匯出"


def main():
    EXPORTS.mkdir(parents=True, exist_ok=True)
    for path in EXPORTS.glob("slide_*.png"):
        path.unlink()

    app = win32com.client.DispatchEx("PowerPoint.Application")
    app.Visible = 1
    presentation = None
    try:
        presentation = app.Presentations.Open(str(PPTX.resolve()), False, False, False)
        for index in range(1, presentation.Slides.Count + 1):
            presentation.Slides(index).Export(str(EXPORTS / f"slide_{index:02d}.png"), "PNG", 1920, 1080)
    finally:
        if presentation is not None:
            presentation.Close()
        app.Quit()

    print(EXPORTS)


if __name__ == "__main__":
    main()
