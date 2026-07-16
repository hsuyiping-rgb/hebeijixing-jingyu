from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import build_lesson_deck as deck


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "output" / "圖片" / "GPT插圖"
OUT = ROOT / "output" / "新媒體" / "貼文包_消防課地域公共性_20260716"
CAROUSEL_DIR = OUT / "圖片_4比5輪播"
REELS_DIR = OUT / "圖片_Reels直式字卡"
YOUTUBE_URL = "https://youtu.be/0s5P7vTrlaU"

GREEN = (31, 71, 47)
MINT = (239, 245, 237)
INK = (32, 38, 36)
GOLD = (204, 151, 54)
WHITE = (255, 255, 255)


def font(size: int, bold: bool = False):
    path = "C:/Windows/Fonts/msjhbd.ttc" if bold else "C:/Windows/Fonts/msjh.ttc"
    return ImageFont.truetype(path, size)


def fit_cover(image_path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, font_obj, fill, spacing=10):
    # Chinese text has no spaces, so textwrap with break_long_words disabled
    # cannot safely wrap it.  Split by character count for predictable frames.
    lines = []
    for paragraph in text.split("\n"):
        chunks = [paragraph[i : i + width] for i in range(0, len(paragraph), width)]
        for chunk in chunks:
            if lines and chunk and chunk[0] in "，。！？：；、」』）】?!.":
                lines[-1] += chunk[0]
                chunk = chunk[1:]
            if chunk:
                lines.append(chunk)
    lines = lines or [text]
    draw.multiline_text(xy, "\n".join(lines), font=font_obj, fill=fill, spacing=spacing)
    return lines


def round_paste(canvas: Image.Image, image: Image.Image, xy: tuple[int, int], radius: int = 30):
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *image.size), radius=radius, fill=255)
    canvas.paste(image, xy, mask)


def make_carousel():
    cards = [
        (1, "當孩子說：\n「我不想加入消防團」", "一堂課，從消防知識走進地域公共性。"),
        (3, "不是知識不足", "孩子正在處理責任、家庭感受與真實生活的衝突。"),
        (8, "從「不想加入」\n回到地域安全", "當沒有人成為消防團員，誰來守護社區？"),
        (12, "一堂可以繼續追問的課", "觀看完整公開課與分析，加入下一輪對話。"),
    ]
    for order, (slide_no, title, body) in enumerate(cards, 1):
        canvas = Image.new("RGB", (1080, 1350), MINT)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 1080, 115), fill=GREEN)
        draw.text((58, 34), f"和北極星境遇  |  0{order}", font=font(30), fill=(226, 234, 220))
        draw.multiline_text((62, 160), title, font=font(58, True), fill=GREEN, spacing=10)
        image = fit_cover(IMAGE_DIR / f"slide_{slide_no:02d}.png", (956, 560))
        round_paste(canvas, image, (62, 390))
        draw.rounded_rectangle((62, 992, 1018, 1192), radius=24, fill=WHITE, outline=(211, 222, 207), width=2)
        draw_wrapped(draw, body, (98, 1030), 19, font(34, True), INK, spacing=10)
        draw.text((62, 1242), YOUTUBE_URL, font=font(23), fill=GREEN)
        canvas.save(CAROUSEL_DIR / f"輪播_{order:02d}.png", quality=95)


def make_reels_frames():
    for index, item in enumerate(deck.slides, 1):
        canvas = Image.new("RGB", (1080, 1920), MINT)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 1080, 130), fill=GREEN)
        draw.text((58, 38), f"公開課觀察  |  {index:02d}/12", font=font(32), fill=(226, 234, 220))
        title = item["title"]
        draw_wrapped(draw, title, (62, 185), 14, font(56, True), GREEN, spacing=12)
        image = fit_cover(IMAGE_DIR / f"slide_{index:02d}.png", (956, 720))
        round_paste(canvas, image, (62, 520))
        draw.rounded_rectangle((62, 1300, 1018, 1555), radius=28, fill=WHITE, outline=(211, 222, 207), width=2)
        line1, line2 = deck.claim_lines_for(index)
        draw.text((104, 1360), line1, font=font(43, True), fill=INK)
        draw.text((104, 1430), line2, font=font(43, True), fill=INK)
        draw.text((62, 1660), "完整公開課與分析", font=font(32, True), fill=GREEN)
        draw.text((62, 1720), YOUTUBE_URL, font=font(25), fill=GREEN)
        draw.text((62, 1818), "插圖為 GPT 生成示意圖，非課堂紀實照片。", font=font(22), fill=(82, 100, 88))
        canvas.save(REELS_DIR / f"reels_{index:02d}.png", quality=95)


def write_copy():
    (OUT / "FB.txt").write_text(
        """孩子明明知道消防團很重要，為什麼仍會說：「我不想加入」？

這堂日本公開課沒有急著把學生拉回標準答案，而是從消防團員缺額、家長問卷與地域安全的真實情境出發，讓孩子重新思考：當社區需要有人承擔時，我與家人可以怎麼參與？

課堂裡珍貴的，不是立刻同意加入，而是孩子願意把家庭感受、公共責任與資料證據放在一起討論。

完整公開課與分析：
https://youtu.be/0s5P7vTrlaU

#學習共同體 #公開觀課 #社會課 #地域公共性 #消防教育 #課例研究
""",
        encoding="utf-8",
    )
    (OUT / "IG.txt").write_text(
        """「消防團很重要，但我不希望爸爸媽媽加入。」

這不是錯誤答案，而是一個孩子正把公共責任放回自己的生活世界。

從消防團缺額、家長問卷，到「如果沒有人加入會怎樣？」這堂課讓孩子在資料、情感與地域安全之間來回思考。

完整公開課與分析
https://youtu.be/0s5P7vTrlaU

#學習共同體 #公開課 #課例研究 #社會課 #地域公共性 #消防教育 #教育現場 #觀課筆記
""",
        encoding="utf-8",
    )
    (OUT / "Reels說明.txt").write_text(
        """當孩子說「我不想加入消防團」，課堂可以怎麼接住這句話？

完整公開課與分析：https://youtu.be/0s5P7vTrlaU

#學習共同體 #公開觀課 #地域公共性 #消防教育 #課例研究
""",
        encoding="utf-8",
    )
    (OUT / "Reels腳本.txt").write_text(
        """片長：約 39 秒

0-03 秒：當孩子說：「我不想加入消防團」
03-09 秒：這不是知識不足，而是責任與家庭感受的衝突。
09-18 秒：從消防團員、家長問卷與地域資料，重新看見公共性。
18-29 秒：如果沒有人加入，地域安全會怎樣？
29-36 秒：高品質課題，不急著收束成標準答案。
36-39 秒：完整公開課與分析，連結見說明欄。

畫面素材為 GPT 生成插圖，非課堂紀實照片。
""",
        encoding="utf-8",
    )
    (OUT / "網址與素材說明.md").write_text(
        f"""# 網址與素材說明

- 原始公開課影片：{YOUTUBE_URL}
- 插圖來源：`output/圖片/GPT插圖/`
- 插圖性質：GPT 生成之課堂情境示意圖，非真實學生或現場紀錄。
- 建議發布：輪播圖使用 `圖片_4比5輪播/`；短影音使用 `reels_消防課地域公共性_直式.mp4`。
""",
        encoding="utf-8",
    )


def write_checklist():
    (OUT / "發布清單.md").write_text(
        """# 發布清單｜消防課的地域公共性

| 平台 | 文案 | 素材 | 建議時間 |
| --- | --- | --- | --- |
| Facebook | `FB.txt` | `圖片_4比5輪播/輪播_01.png` 至 `輪播_04.png` | 晚上 20:00-22:00 |
| Instagram | `IG.txt` | `圖片_4比5輪播/輪播_01.png` 至 `輪播_04.png` | 晚上 20:00-22:00 |
| Reels | `Reels說明.txt` | `reels_消防課地域公共性_直式.mp4` | 週末白天 |

## 發布前

- [ ] 確認影片網址可正常開啟。
- [ ] 保留「GPT 生成示意圖，非課堂紀實照片」說明。
- [ ] 依粉專名稱調整 hashtag。
- [ ] 預覽 Reels 封面與底部安全區。
""",
        encoding="utf-8",
    )


def main():
    for folder in (OUT, CAROUSEL_DIR, REELS_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    make_carousel()
    make_reels_frames()
    write_copy()
    write_checklist()
    shutil.copy2(REELS_DIR / "reels_01.png", OUT / "Reels封面_1080x1920.png")
    print(OUT)


if __name__ == "__main__":
    main()
