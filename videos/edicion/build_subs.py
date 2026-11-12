import json, re, sys
from PIL import Image, ImageDraw, ImageFont

S = sys.argv[1]
tx = json.load(open(f"{S}/tx/cut5812_medium.json"))

# --- words -------------------------------------------------------------
words = []
for seg in tx["segments"]:
    for w in seg["words"]:
        t = w["word"].strip()
        if t:
            words.append({"w": t, "s": w["start"], "e": w["end"]})

def norm(t):
    return re.sub(r"[^\wáéíóúñü]", "", t.lower())

# corrections: (sequence of normalized source words) -> replacement tokens
FIX = [
    (["me", "voy", "a", "desplayar"], ["me", "voy", "a", "explayar"]),
    (["un", "pie", "que"], ["un", "pibe", "que"]),
    (["le", "viene", "el", "laburo"], ["le", "va", "bien", "en", "el", "laburo,"]),
    (["que", "que", "entrena"], ["que", "entrena,"]),
    (["tiempo", "que", "aleja", "con"], ["tiempo", "de", "calidad", "con"]),
    (["tiempo", "que", "aliás", "con"], ["tiempo", "de", "calidad", "con"]),
    (["te", "esperas", "que", "caiga", "el", "cielo"], ["¿te", "esperás", "que", "caiga", "del", "cielo?"]),
    (["imítalo"], ["invitalo"]),
    (["verse", "a", "esas"], ["verte", "con", "esas"]),
    (["salía", "la", "vida", "real", "conocés"], ["salí", "a", "la", "vida", "real,", "conocé"]),
    (["te", "pases", "a", "los", "estrellas", "de", "la", "mañana"], ["te", "pases", "hasta", "las", "3", "de", "la", "mañana"]),
    (["hablando", "por", "los", "auriculares"], ["con", "los", "auriculares"]),
    (["necesitas"], ["necesitás"]),
    (["propone"], ["proponé"]),
    (["pasa", "tiempo", "que", "aliás", "con"], ["pasá", "tiempo", "de", "calidad", "con"]),
    (["fíjate"], ["fijate"]),
    (["quedas"], ["quedás"]),
    (["háblale"], ["hablale"]),
    (["reírte"], ["reírte"]),
]

i = 0
out = []
while i < len(words):
    done = False
    for src, dst in FIX:
        n = len(src)
        if [norm(x["w"]) for x in words[i:i + n]] == src:
            s, e = words[i]["s"], words[i + n - 1]["e"]
            step = (e - s) / len(dst)
            for k, d in enumerate(dst):
                out.append({"w": d, "s": s + k * step, "e": s + (k + 1) * step})
            i += n
            done = True
            break
    if not done:
        out.append(words[i]); i += 1
words = out

# --- chunking ----------------------------------------------------------
chunks, cur = [], []
for idx, w in enumerate(words):
    cur.append(w)
    txt = " ".join(x["w"] for x in cur)
    nxt = words[idx + 1] if idx + 1 < len(words) else None
    gap = (nxt["s"] - w["e"]) if nxt else 9
    punct = re.search(r"[.,?!…]$", w["w"])
    if len(cur) >= 3 or len(txt) >= 12 or punct or gap > 0.25 or \
       (nxt and len(txt) + 1 + len(nxt["w"]) > 15):
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
merged=[]
for ch in chunks:
    if merged and (ch[0]["s"]-merged[-1][0]["s"])<0.25 and len(merged[-1])+len(ch)<=4:
        merged[-1]=merged[-1]+ch
    else: merged.append(ch)
chunks=merged

KEY = re.compile(r"^(amig\w*|matemátic\w*|calidad|horas?|tiempo|vínculo\w*|kansas|2018|50|90|200|3|repetici\w*|solo|planes|real)$", re.I)

def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

lines = []
for ci, ch in enumerate(chunks):
    st = ch[0]["s"]
    en = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.4
    en = min(en, ch[-1]["e"] + 0.5)
    if en - st < 0.2: en = st + 0.2
    parts = []
    for w in ch:
        t = re.sub(r"[.,…]+$", "", w["w"]).upper()
        if KEY.match(norm(w["w"])):
            parts.append(r"{\c&H00D4FF&}" + t + r"{\c&HFFFFFF&}")
        else:
            parts.append(t)
    text = " ".join(parts)
    pop = r"{\fscx85\fscy85\t(0,90,\fscx100\fscy100)}"
    lines.append(f"Dialogue: 0,{fmt(st)},{fmt(en)},Sub,,0,0,0,,{pop}{text}")

ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat Black,98,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,8,3,2,50,50,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(f"{S}/cut/subs5812.ass", "w").write(ass + "\n".join(lines) + "\n")
open(f"{S}/cut/subs5812.txt", "w").write("\n".join(
    f"{fmt(c[0]['s'])}  " + " ".join(x['w'] for x in c) for c in chunks))
print(len(chunks), "chunks; min dur check:",
      min((chunks[i+1][0]['s'] if i+1 < len(chunks) else 999) - c[0]['s'] for i, c in enumerate(chunks)))

# --- title PNG -----------------------------------------------------------
L1, L2 = "¿NO TENÉS AMIGOS?", "ES PURA MATEMÁTICA"
font = ImageFont.truetype(f"{S}/fonts/Montserrat-900.ttf", 74)
img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
y = 150
for txt, bg, fg in [(L1, (255, 255, 255, 255), (0, 0, 0, 255)), (L2, (255, 212, 0, 255), (0, 0, 0, 255))]:
    bb = d.textbbox((0, 0), txt, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    padx, pady = 34, 22
    x0 = (1080 - w) // 2 - padx
    d.rounded_rectangle([x0, y, x0 + w + 2 * padx, y + h + 2 * pady], radius=22, fill=bg)
    d.text(((1080 - w) // 2 - bb[0], y + pady - bb[1]), txt, font=font, fill=fg)
    y += h + 2 * pady + 14
img.save(f"{S}/cut/title5812.png")
print("title bottom y =", y)
