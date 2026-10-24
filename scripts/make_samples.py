"""Render Veyo's original example creatives. These are ads, never synthetic predictions."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "public" / "samples"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 900, 1125


def font(size, bold=False):
    candidates = [f"/System/Library/Fonts/Supplemental/Arial{' Bold' if bold else ''}.ttf",
                  f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def text(draw, at, value, size=30, color="#263326", bold=False):
    draw.text(at, value, font=font(size, bold), fill=color, spacing=0)


def shadow(image, bounds, blur=18, opacity=35):
    layer = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(layer)
    draw.ellipse(bounds, fill=(20, 30, 15, opacity))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def forma():
    image = Image.new("RGBA", (W, H), "#efeee6")
    d = ImageDraw.Draw(image)
    d.rectangle((0, 370, W, 995), fill="#d9dfce")
    d.ellipse((-330, 270, 620, 1260), fill="#e5e8db")
    d.ellipse((590, 670, 1200, 1300), fill="#cbd4bc")
    text(d, (56, 47), "forma", 75, bold=True)
    text(d, (700, 73), "DAILY / 01", 15)
    text(d, (59, 177), "Less, but better.", 68, bold=True)
    text(d, (63, 268), "Everyday care. Nothing extra.", 28, color="#65705e")
    for x, y, w, h, cap, label in [(190, 552, 150, 330, 70, "THE WASH"), (370, 439, 176, 445, 85, "THE SERUM"), (573, 602, 141, 282, 50, "THE CREAM")]:
        shadow(image, (x-25, y+h-12, x+w+55, y+h+45))
        d = ImageDraw.Draw(image)
        d.rounded_rectangle((x, y, x+w, y+h), radius=17, fill="#f9f8f1", outline="#ccd0c1", width=2)
        d.rounded_rectangle((x+14, y-cap+5, x+w-14, y+20), radius=9, fill="#394334")
        d.rectangle((x+20, y+int(h*.33), x+w-20, y+int(h*.76)), fill="#e8ebdf")
        text(d, (x+29, y+int(h*.36)), "f.", 45, bold=True)
        text(d, (x+28, y+int(h*.58)), label, 13, bold=True)
        text(d, (x+28, y+int(h*.65)), "EVERY DAY", 10, color="#6c7563")
        d.line((x+10, y+25, x+10, y+h-23), fill="#ffffff", width=4)
    d = ImageDraw.Draw(image)
    text(d, (60, 1037), "Good for your skin. Easier on your shelf.", 25)
    text(d, (747, 1043), "forma.co", 16)
    image.convert("RGB").save(OUT / "forma.png", optimize=True)


def fieldwork():
    image = Image.new("RGBA", (W, H), "#efe4d4")
    d = ImageDraw.Draw(image)
    d.ellipse((-50, 330, 970, 1350), fill="#bd7146")
    d.ellipse((330, 550, 1090, 1310), fill="#a65e3b")
    text(d, (54, 52), "FIELDWORK", 49, "#453224", True)
    text(d, (663, 73), "SMALL BATCH", 16, "#6f513b")
    text(d, (57, 180), "A better morning.", 68, "#453224", True)
    text(d, (62, 276), "Good coffee. A slower start.", 28, "#70553f")
    shadow(image, (214, 872, 760, 970), 28, 65)
    d = ImageDraw.Draw(image)
    d.polygon([(278, 420), (605, 420), (656, 905), (622, 950), (246, 950)], fill="#30382a")
    d.polygon([(278, 420), (300, 380), (583, 380), (605, 420)], fill="#3d4634")
    d.line((290, 425, 594, 425), fill="#647056", width=5)
    d.rounded_rectangle((285, 540, 616, 835), radius=3, fill="#f4e9d9")
    text(d, (313, 568), "FIELDWORK", 33, "#39432f", True)
    text(d, (317, 626), "MORNING", 39, "#39432f", True)
    text(d, (317, 677), "RITUAL", 39, "#39432f", True)
    d.line((317, 746, 582, 746), fill="#a5ae91", width=1)
    text(d, (317, 770), "COLOMBIA / WHOLE BEAN", 14, "#687251")
    for x, y, size in [(140, 901, 19), (713, 890, 22), (749, 931, 16), (185, 954, 13), (691, 979, 14)]:
        d.ellipse((x, y, x+size*2, y+size), fill="#573b27")
        d.line((x+4, y+size//2, x+size*2-4, y+size//2), fill="#986948", width=2)
    text(d, (60, 1045), "Make room for the ritual.", 29, "#fff2e3", True)
    text(d, (716, 1052), "250 G", 18, "#fff2e3")
    image.convert("RGB").save(OUT / "fieldwork.png", optimize=True)


def pace():
    image = Image.new("RGB", (W, H), "#dfe5ed")
    d = ImageDraw.Draw(image)
    d.rectangle((0, 580, W, H), fill="#e45e38")
    d.ellipse((-500, 510, 1010, 2020), fill="#c84829")
    for offset in [0, 65, 130, 195, 260]:
        d.arc((-555+offset, 510+offset, 1010-offset, 2075-offset), 180, 350, fill="#f3b69f", width=5)
    text(d, (56, 51), "PACE.", 68, "#253448", True)
    text(d, (652, 76), "YOUR EVERYDAY RUN", 13, "#435267", True)
    text(d, (52, 183), "FIND YOUR", 97, "#253448", True)
    text(d, (52, 303), "OWN", 97, "#253448", True)
    text(d, (52, 423), "RHYTHM.", 97, "#253448", True)
    text(d, (610, 631), "NO CLOCK.", 21, "#fff1e7", True)
    text(d, (610, 668), "NO COMPARISON.", 21, "#fff1e7", True)
    text(d, (610, 705), "JUST YOU.", 21, "#fff1e7", True)
    d.rounded_rectangle((55, 1000, 385, 1076), radius=38, fill="#f6f0e9")
    text(d, (88, 1021), "FIND YOUR PACE", 25, "#263448", True)
    text(d, (664, 1038), "pace.run", 21, "#fff1e7", True)
    image.save(OUT / "pace.png", optimize=True)


if __name__ == "__main__":
    forma(); fieldwork(); pace()
    print("Rendered three original example creatives.")
