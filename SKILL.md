---
name: full-deck
description: "テーマを入力するだけで、イラスト埋め込み済み統合スライドPDF（8枚）＋個別イラストPNGを一括生成するスキル。"
version: "2.1.0"
author: user
license: MIT

category: presentation
tags:
  - slides
  - illustration
  - pdf
  - png
  - all-in-one
department: All

models:
  recommended:
    - claude-sonnet-4-6
    - claude-opus-4

languages:
  - ja
---

# full-deck スキル

## 概要

テーマとページ数を入力するだけで、以下を**1回の実行でまとめて生成**します。

| 出力ファイル | 内容 |
|------------|------|
| `[テーマ]_スライド.pdf` | **統合PDF**（ページ数に応じたテキスト＋イラスト埋め込み） |
| `[テーマ]_step.png` | ステップ図（使い方・手順） |
| `[テーマ]_comparison.png` | Before/After 比較図 |
| `[テーマ]_badge.png` | 数値・アイコンバッジ |

### ページ数別スライド構成

| ページ数 | 構成 |
|---------|------|
| **3枚** | intro → illust(comparison) → warnings |
| **5枚** | intro → before → bullets → categories → warnings |
| **6枚** | intro → before → illust(comparison) → bullets → categories → warnings |
| **8枚（デフォルト）** | intro → before → illust(comparison) → bullets → illust(step) → categories → warnings → illust(badge) |
| **カスタム** | ページ数に応じてClaudeが最適な構成を決定 |

---

## 動作フロー

### Step 1: ヒアリング（AskUserQuestion で2問）

```
質問1: テーマと対象者
  例：「Notion活用法・初心者向け」「副業の始め方・会社員向け」

質問2: ページ数
  選択肢: 3枚（ショート）/ 5枚（標準）/ 6枚 / 8枚（フル・デフォルト）/ カスタム入力
```

### Step 2: ページ数に応じた全コンテンツを一括設計

指定されたページ数に基づいて以下の表から `slides` 配列を構成する。

**ページ数別 slides 構成テンプレート:**

```
■ 3枚
slides = [
  { "type": "intro",    "page": 1, ... },
  { "type": "illust",   "page": 2, "illust_type": "comparison", ... },
  { "type": "warnings", "page": 3, ... },
]

■ 5枚
slides = [
  { "type": "intro",       "page": 1, ... },
  { "type": "before",      "page": 2, ... },
  { "type": "bullets",     "page": 3, ... },
  { "type": "categories",  "page": 4, ... },
  { "type": "warnings",    "page": 5, ... },
]

■ 6枚
slides = [
  { "type": "intro",       "page": 1, ... },
  { "type": "before",      "page": 2, ... },
  { "type": "illust",      "page": 3, "illust_type": "comparison", ... },
  { "type": "bullets",     "page": 4, ... },
  { "type": "categories",  "page": 5, ... },
  { "type": "warnings",    "page": 6, ... },
]

■ 8枚（デフォルト）
slides = [
  { "type": "intro",       "page": 1, ... },
  { "type": "before",      "page": 2, ... },
  { "type": "illust",      "page": 3, "illust_type": "comparison", ... },
  { "type": "bullets",     "page": 4, ... },
  { "type": "illust",      "page": 5, "illust_type": "step",       ... },
  { "type": "categories",  "page": 6, ... },
  { "type": "warnings",    "page": 7, ... },
  { "type": "illust",      "page": 8, "illust_type": "badge",      ... },
]

■ カスタム（例: 10枚）
  上記スライドタイプを組み合わせ、テーマに最適な構成をClaudeが決定する。
  illust型は3種類（comparison/step/badge）を適切なタイミングに配置する。
```

**イラスト3点（ページ数に関わらず常に生成・使用する分だけPDFに埋め込み）:**
```
step図      → テーマの「始め方3〜4ステップ」
comparison  → テーマ「なし」vs「あり」の対比
badge       → テーマの効果を表す3つの数値・キーワード
```

### Step 3: 1本のPythonスクリプトを生成・実行

**`generate_all()` の処理順序（重要）:**
1. イラストPNGを先に生成・保存（3種類すべて）
2. `illust`型スライドの`_img_path`に保存先パスを注入
3. `generate_slides()`で指定ページ数分のPDFを一括生成（`c.drawImage()`で埋め込み）

---

## Pythonベースコード（v2: イラスト埋め込み統合版）

```python
import os
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import stringWidth
except ImportError:
    os.system("pip install reportlab")
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import stringWidth

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    os.system("pip install Pillow")
    from PIL import Image, ImageDraw, ImageFont

# =========================================================
# カラー定数（師匠PDFデザイン）
# =========================================================
RL_BG      = HexColor("#E0F7FA")
RL_HEADER  = HexColor("#00828E")
RL_DARK    = HexColor("#005F63")
RL_ACCENT  = HexColor("#FF6F42")
RL_TEXT    = HexColor("#37464F")
RL_DIVIDER = HexColor("#CCE8EB")
RL_WHITE   = HexColor("#FFFFFF")

PIL_BG     = (224, 247, 250)
PIL_TEAL   = (0, 130, 142)
PIL_ORANGE = (255, 111, 66)
PIL_DARK   = (55, 70, 79)
PIL_WHITE  = (255, 255, 255)
PIL_GRAY   = (200, 210, 215)

# =========================================================
# フォント
# =========================================================
FONT_CANDIDATES = [
    # Windows
    ("C:/Windows/Fonts/meiryo.ttc",   "Meiryo"),
    ("C:/Windows/Fonts/msgothic.ttc", "MSGothic"),
    ("C:/Windows/Fonts/YuGothR.ttc",  "YuGothic"),
    # Mac
    ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", "HiraginoKaku"),
    # Linux: IPAフォント（TTFアウトライン・reportlab対応）
    ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",    "IPAGothic"),
    ("/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf","IPAexGothic"),
    ("/usr/share/fonts/truetype/ipafont/ipag.ttf",           "IPAGothic2"),
    ("/usr/share/fonts/ipa/ipag.ttf",                        "IPAGothic3"),
]
FONT_PATH = next((p for p, _ in FONT_CANDIDATES if os.path.exists(p)), None)

# マスコット画像（右下に配置）※不要な場合は None に
MASCOT_PATH = r"C:\Users\haiki\OneDrive\デスクトップ\スキル\スキル開発\スライド\hamster.png"

def setup_rl_fonts():
    for path, name in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                try:
                    pdfmetrics.registerFont(TTFont(name+"-Bold", path, subfontIndex=1))
                except:
                    pdfmetrics.registerFont(TTFont(name+"-Bold", path))
                return name
            except:
                continue
    return "Helvetica"

RL_FONT      = setup_rl_fonts()
RL_FONT_BOLD = RL_FONT + "-Bold" if RL_FONT != "Helvetica" else "Helvetica-Bold"

def pil_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size) if FONT_PATH else ImageFont.load_default()
    except:
        return ImageFont.load_default()

# =========================================================
# PART 1: スライド描画（reportlab）
# =========================================================
W_SL, H_SL  = 960, 540
HEADER_H    = 85
FOOTER_H    = 28
SL_MARGIN   = 50
BODY_TOP    = H_SL - HEADER_H - 8
BODY_BOTTOM = FOOTER_H + 8
BODY_H      = BODY_TOP - BODY_BOTTOM

def sl_wrap(text, fn, fs, mw):
    lines, cur = [], ""
    for ch in text:
        if stringWidth(cur+ch, fn, fs) <= mw:
            cur += ch
        else:
            if cur: lines.append(cur)
            cur = ch
    if cur: lines.append(cur)
    return lines

def sl_draw_wrapped(c, text, x, y, fn, fs, color, mw, ml=99):
    c.setFillColor(color); c.setFont(fn, fs)
    for ln in sl_wrap(text, fn, fs, mw)[:ml]:
        c.drawString(x, y, ln); y -= fs+4
    return y

def sl_bg(c):
    c.setFillColor(RL_BG); c.rect(0, 0, W_SL, H_SL, fill=1, stroke=0)

def sl_header(c, title):
    c.setFillColor(RL_HEADER); c.rect(0, H_SL-HEADER_H, W_SL, HEADER_H, fill=1, stroke=0)
    c.setFillColor(RL_ACCENT); c.rect(0, H_SL-HEADER_H, 8, HEADER_H, fill=1, stroke=0)
    c.setFillColor(RL_WHITE);  c.setFont(RL_FONT_BOLD, 32)
    c.drawString(SL_MARGIN, H_SL-HEADER_H+25, title)

def sl_footer(c, pg, total, theme):
    c.setFillColor(RL_DARK); c.rect(0, 0, W_SL, FOOTER_H, fill=1, stroke=0)
    c.setFillColor(RL_WHITE); c.setFont(RL_FONT, 11)
    c.drawString(SL_MARGIN, 8, theme)
    c.drawRightString(W_SL-SL_MARGIN, 8, f"{pg} / {total}")

def sl_card(c, x, y, w, h):
    c.setFillColor(RL_WHITE); c.rect(x, y, w, h, fill=1, stroke=0)

def sl_divider(c, x, y, w):
    c.setStrokeColor(RL_DIVIDER); c.setLineWidth(1); c.line(x, y, x+w, y)

def sl_mascot(c):
    """マスコット画像を右下に描画する"""
    if MASCOT_PATH and os.path.exists(MASCOT_PATH):
        mh = 90
        c.drawImage(MASCOT_PATH, W_SL - mh - 8, FOOTER_H + 2, mh, mh,
                    preserveAspectRatio=True, mask='auto')

# ---------- slide_intro: 動的スロット配置でbulletsを均等分散 ----------
def slide_intro(c, data):
    sl_bg(c); sl_header(c, data['title']); sl_footer(c, data['page'], data['total'], data['theme'])
    GAP, pad = 14, 16
    col_w = (W_SL - SL_MARGIN*2 - GAP*2) // 3
    tw    = col_w - pad*2
    for i, pt in enumerate(data['points'][:3]):
        x = SL_MARGIN + i*(col_w+GAP); cy = BODY_BOTTOM
        sl_card(c, x, cy, col_w, BODY_H)
        c.setFillColor(RL_ACCENT); c.rect(x, cy+BODY_H-8, col_w, 8, fill=1, stroke=0)
        c.setFillColor(RL_HEADER); c.setFont(RL_FONT_BOLD, 20)
        c.drawString(x+pad, cy+BODY_H-34, pt['label'])
        if pt.get('tagline'):
            c.setFillColor(RL_ACCENT); c.setFont(RL_FONT, 13)
            c.drawString(x+pad, cy+BODY_H-54, pt['tagline'])
        sl_divider(c, x+pad, cy+BODY_H-64, tw)
        # 利用可能な高さを箇条書き数で均等分割して配置
        bullets_list = [b for b in pt.get('bullets', []) if b]
        n_b = len(bullets_list)
        if n_b > 0:
            area_top    = cy + BODY_H - 72
            area_bottom = cy + 16
            slot_h      = (area_top - area_bottom) // n_b
            for idx, b in enumerate(bullets_list):
                slot_top = area_top - slot_h * idx
                by       = slot_top - max(6, (slot_h - 20) // 2)
                lines    = sl_wrap(b, RL_FONT, 14, tw-20)
                c.setFillColor(RL_ACCENT); c.setFont(RL_FONT_BOLD, 16)
                c.drawString(x+pad, by, "•")
                c.setFillColor(RL_TEXT); c.setFont(RL_FONT, 14)
                for j, ln in enumerate(lines[:2]):
                    c.drawString(x+pad+18, by-j*18, ln)
    sl_mascot(c)
    c.showPage()

# ---------- slide_before: 動的スロット配置でpointsを均等分散 ----------
def slide_before(c, data):
    sl_bg(c); sl_header(c, data['title']); sl_footer(c, data['page'], data['total'], data['theme'])
    items = data['items']; n = len(items)
    GAP, pad = 16, 14
    col_w   = (W_SL - SL_MARGIN*2 - GAP*(n-1)) // n
    tw      = col_w - pad*2
    concl_h = 38 if data.get('conclusion') else 0
    ch      = BODY_H - concl_h - (8 if concl_h else 0)
    card_y  = BODY_BOTTOM + concl_h + (8 if concl_h else 0)
    for i, item in enumerate(items):
        x = SL_MARGIN + i*(col_w+GAP)
        sl_card(c, x, card_y, col_w, ch)
        c.setFillColor(RL_HEADER); c.rect(x, card_y+ch-40, col_w, 40, fill=1, stroke=0)
        c.setFillColor(RL_ACCENT); c.rect(x, card_y+ch-40, 6, 40, fill=1, stroke=0)
        lsz = 17 if stringWidth(item['label'], RL_FONT_BOLD, 17) <= tw-10 else 14
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, lsz)
        c.drawString(x+pad+4, card_y+ch-26, item['label'])
        ty = card_y+ch-58
        desc_end = sl_draw_wrapped(c, item['desc'], x+pad, ty, RL_FONT, 14, RL_TEXT, tw, ml=3)
        div_y = desc_end - 14
        sl_divider(c, x+pad, div_y, tw)
        # 区切り線〜カード下部を均等分割して配置
        if item.get('points'):
            pts_top    = div_y - 14
            pts_bottom = card_y + 12
            n_p     = len(item['points'])
            slot_p  = (pts_top - pts_bottom) // max(n_p, 1)
            for idx, pt_text in enumerate(item['points']):
                slot_top = pts_top - slot_p * idx
                py       = slot_top - max(4, (slot_p - 18) // 2)
                lns      = sl_wrap(pt_text, RL_FONT, 13, tw-20)
                c.setFillColor(RL_ACCENT); c.setFont(RL_FONT_BOLD, 15)
                c.drawString(x+pad, py, "›")
                c.setFillColor(RL_TEXT); c.setFont(RL_FONT, 13)
                for j, ln in enumerate(lns[:2]):
                    c.drawString(x+pad+16, py-j*16, ln)
                if py - 32 < card_y+10: break
    if data.get('conclusion'):
        c.setFillColor(RL_ACCENT); c.rect(SL_MARGIN, BODY_BOTTOM, W_SL-SL_MARGIN*2, concl_h, fill=1, stroke=0)
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, 15)
        c.drawCentredString(W_SL/2, BODY_BOTTOM+12, data['conclusion'])
    sl_mascot(c)
    c.showPage()

# ---------- slide_illust: PNG画像をスライドに埋め込む ----------
def slide_illust(c, data):
    """生成済みイラストPNGをスライド本文エリア全体に埋め込む"""
    sl_bg(c)
    sl_header(c, data['title'])
    sl_footer(c, data['page'], data['total'], data['theme'])
    img_path = data.get('_img_path', '')
    if img_path and os.path.exists(img_path):
        pad = 16
        avail_w = W_SL - SL_MARGIN*2 - pad*2
        avail_h = BODY_H - pad*2
        ir = ImageReader(img_path)
        iw, ih = ir.getSize()
        scale = min(avail_w/iw, avail_h/ih)
        dw, dh = iw*scale, ih*scale
        dx = (W_SL - dw) / 2
        dy = BODY_BOTTOM + pad + (avail_h - dh) / 2
        # 白いカード背景
        c.setFillColor(RL_WHITE)
        c.rect(SL_MARGIN, BODY_BOTTOM+pad//2,
               W_SL-SL_MARGIN*2, BODY_H-pad, fill=1, stroke=0)
        c.drawImage(img_path, dx, dy, dw, dh,
                    preserveAspectRatio=True, mask='auto')
    sl_mascot(c)
    c.showPage()

def slide_bullets(c, data):
    sl_bg(c); sl_header(c, data['title']); sl_footer(c, data['page'], data['total'], data['theme'])
    bullets = data['bullets']; n = len(bullets)
    ch_     = 36 if data.get('conclusion') else 0
    avail_h = BODY_H - ch_ - (6 if ch_ else 0)
    item_h  = (avail_h - 6*(n-1)) // n
    cw      = W_SL - SL_MARGIN*2; tw = cw - 60
    y_top   = BODY_TOP - 6
    for bi, b in enumerate(bullets):
        cy = y_top - (item_h+6)*bi - item_h
        sl_card(c, SL_MARGIN, cy, cw, item_h)
        c.setFillColor(RL_HEADER); c.rect(SL_MARGIN, cy, 5, item_h, fill=1, stroke=0)
        main_y = cy+item_h-22
        title  = b['title'] if isinstance(b, dict) else b
        c.setFillColor(RL_HEADER); c.setFont(RL_FONT_BOLD, 17); c.drawString(SL_MARGIN+20, main_y, title)
        if isinstance(b, dict) and b.get('desc'):
            sl_draw_wrapped(c, b['desc'], SL_MARGIN+20, main_y-22, RL_FONT, 13, RL_TEXT, tw, ml=2)
    if data.get('conclusion'):
        c.setFillColor(RL_ACCENT); c.rect(SL_MARGIN, BODY_BOTTOM, cw, ch_, fill=1, stroke=0)
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, 15)
        c.drawCentredString(W_SL/2, BODY_BOTTOM+11, data['conclusion'])
    sl_mascot(c)
    c.showPage()

def slide_categories(c, data):
    sl_bg(c); sl_header(c, data['title']); sl_footer(c, data['page'], data['total'], data['theme'])
    cats = data['categories']
    GAP, pad = 14, 14
    col_w  = (W_SL - SL_MARGIN*2 - GAP*2) // 3
    tw     = col_w - pad*2
    ch_    = 36 if data.get('conclusion') else 0
    card_h = BODY_H - ch_ - (8 if ch_ else 0)
    card_y = BODY_BOTTOM + ch_ + (8 if ch_ else 0)
    for i, cat in enumerate(cats[:3]):
        x = SL_MARGIN + i*(col_w+GAP)
        sl_card(c, x, card_y, col_w, card_h)
        c.setFillColor(RL_HEADER); c.rect(x, card_y+card_h-44, col_w, 44, fill=1, stroke=0)
        nsz = 16 if stringWidth(cat['name'], RL_FONT_BOLD, 16) <= tw else 13
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, nsz)
        c.drawCentredString(x+col_w/2, card_y+card_h-30, cat['name'])
        iy = card_y+card_h-64
        for item in cat.get('items', []):
            sl_divider(c, x+pad, iy+4, tw); iy -= 8
            if isinstance(item, dict):
                c.setFillColor(RL_HEADER); c.setFont(RL_FONT_BOLD, 14); c.drawString(x+pad, iy, item['name'])
                iy -= 18
                iy = sl_draw_wrapped(c, item.get('desc',''), x+pad+4, iy, RL_FONT, 12, RL_TEXT, tw-4, ml=3)
                iy -= 6
            if iy < card_y+10: break
    if data.get('conclusion'):
        c.setFillColor(RL_ACCENT); c.rect(SL_MARGIN, BODY_BOTTOM, W_SL-SL_MARGIN*2, ch_, fill=1, stroke=0)
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, 15)
        c.drawCentredString(W_SL/2, BODY_BOTTOM+11, data['conclusion'])
    sl_mascot(c)
    c.showPage()

def slide_warnings(c, data):
    sl_bg(c); sl_header(c, data['title']); sl_footer(c, data['page'], data['total'], data['theme'])
    items = data['items']; n = len(items)
    ch_   = 36 if data.get('conclusion') else 0
    avail = BODY_H - ch_ - (6 if ch_ else 0)
    ih    = (avail - 8*(n-1)) // n
    cw    = W_SL - SL_MARGIN*2; tw = cw - 80
    y_top = BODY_TOP - 6
    for i, item in enumerate(items, 1):
        cy = y_top - (ih+8)*(i-1) - ih
        sl_card(c, SL_MARGIN, cy, cw, ih)
        bx, by = SL_MARGIN+28, cy+ih//2
        c.setFillColor(RL_ACCENT); c.circle(bx, by, 22, fill=1, stroke=0)
        c.setFillColor(RL_WHITE);  c.setFont(RL_FONT_BOLD, 18); c.drawCentredString(bx, by-7, str(i))
        c.setFillColor(RL_HEADER); c.setFont(RL_FONT_BOLD, 18); c.drawString(SL_MARGIN+62, cy+ih-26, item['title'])
        sl_draw_wrapped(c, item['desc'], SL_MARGIN+62, cy+ih-50, RL_FONT, 14, RL_TEXT, tw, ml=3)
    if data.get('conclusion'):
        c.setFillColor(RL_HEADER); c.rect(SL_MARGIN, BODY_BOTTOM, cw, ch_, fill=1, stroke=0)
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, 15)
        c.drawCentredString(W_SL/2, BODY_BOTTOM+11, data['conclusion'])
    sl_mascot(c)
    c.showPage()

def generate_slides(slides_data, output_path):
    c = canvas.Canvas(output_path, pagesize=(W_SL, H_SL))
    total = len(slides_data)
    for slide in slides_data:
        slide['total'] = total
        t = slide.get('type')
        if   t == 'intro':      slide_intro(c, slide)
        elif t == 'before':     slide_before(c, slide)
        elif t == 'bullets':    slide_bullets(c, slide)
        elif t == 'categories': slide_categories(c, slide)
        elif t == 'warnings':   slide_warnings(c, slide)
        elif t == 'illust':     slide_illust(c, slide)
    c.save()
    print(f"  PDF ({total}枚): {output_path}")

# =========================================================
# PART 2: イラスト生成（Pillow）
# =========================================================

def pil_rounded_rect(draw, xy, r, fill):
    x0,y0,x1,y1 = xy
    draw.rectangle([x0+r,y0,x1-r,y1], fill=fill)
    draw.rectangle([x0,y0+r,x1,y1-r], fill=fill)
    for cx,cy in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
        draw.ellipse([cx,cy,cx+2*r,cy+2*r], fill=fill)

def pil_arrow_right(draw, x, y, length, color, th=5):
    ah, aw = th*3, th*4
    if length > aw:
        draw.rectangle([x, y-th//2, x+length-aw, y+th//2], fill=color)
    draw.polygon([(x+length-aw,y-ah//2),(x+length,y),(x+length-aw,y+ah//2)], fill=color)

def pil_text_c(draw, cx, cy, text, fn, fill):
    draw.text((cx, cy), text, font=fn, fill=fill, anchor='mm')

def pil_multiline_c(draw, cx, top, text, fn, fill, lh=20):
    for i, ln in enumerate(text.split('\n')):
        draw.text((cx, top+i*lh), ln, font=fn, fill=fill, anchor='mm')

def make_step_illust(data, output_path):
    steps = data['steps']; n = len(steps)
    W, H  = 900, 300
    img   = Image.new('RGB', (W,H), PIL_BG)
    d     = ImageDraw.Draw(img)
    box_w = min(190, (W-60)//n - 10)
    box_h = 220
    gap   = max(30, (W-60-box_w*n)//(n-1)) if n>1 else 0
    total_w = box_w*n + gap*(n-1)
    sx    = (W-total_w)//2
    if data.get('title'):
        d.text((W//2, 15), data['title'], font=pil_font(18), fill=PIL_TEAL, anchor='mm')
    for i, step in enumerate(steps):
        bx = sx + i*(box_w+gap)
        by = (H-box_h)//2 + (16 if data.get('title') else 0)
        pil_rounded_rect(d, [bx,by,bx+box_w,by+box_h], 14, PIL_WHITE)
        cx_b = bx+box_w//2
        d.ellipse([cx_b-22, by+10, cx_b+22, by+54], fill=PIL_ORANGE)
        pil_text_c(d, cx_b, by+32, step['num'], pil_font(18), PIL_WHITE)
        pil_text_c(d, cx_b, by+72, step.get('title',''), pil_font(15), PIL_TEAL)
        pil_multiline_c(d, cx_b, by+95, step.get('desc',''), pil_font(12), PIL_DARK, lh=17)
        if i < n-1:
            pil_arrow_right(d, bx+box_w+4, H//2+(8 if data.get('title') else 0), gap-8, PIL_TEAL, th=5)
    img.save(output_path)
    print(f"  step PNG: {output_path}")

def make_comparison_illust(data, output_path):
    W, H  = 900, 340
    img   = Image.new('RGB', (W,H), PIL_BG)
    d     = ImageDraw.Draw(img)
    pad   = 36; pw = (W-pad*3)//2; ph = H-pad*2
    panels = [
        (data['before'], pad,      PIL_GRAY,  PIL_DARK),
        (data['after'],  pad*2+pw, PIL_TEAL,  PIL_WHITE),
    ]
    for panel, px, bg, tc in panels:
        pil_rounded_rect(d, [px,pad,px+pw,pad+ph], 16, bg)
        pil_text_c(d, px+pw//2, pad+28, panel['label'], pil_font(20), tc)
        d.line([(px+20,pad+52),(px+pw-20,pad+52)], fill=tc if bg==PIL_GRAY else PIL_WHITE, width=2)
        for j, item in enumerate(panel['items']):
            pil_text_c(d, px+pw//2, pad+82+j*58, item, pil_font(16), tc)
    pil_arrow_right(d, pad+pw+6, H//2, pad*2-12, PIL_ORANGE, th=8)
    img.save(output_path)
    print(f"  comparison PNG: {output_path}")

def make_badge_illust(data, output_path):
    W, H  = 900, 280
    img   = Image.new('RGB', (W,H), PIL_BG)
    d     = ImageDraw.Draw(img)
    items = data['items']; n = len(items)
    xs    = [W*(i+1)//(n+1) for i in range(n)]
    r     = 68
    for cx, item in zip(xs, items):
        cy = H//2 - 10
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=PIL_ORANGE)
        pil_text_c(d, cx, cy-14, item.get('icon',''), pil_font(26), PIL_WHITE)
        pil_text_c(d, cx, cy+18, item['value'],       pil_font(20), PIL_WHITE)
        pil_text_c(d, cx, cy+r+24, item['label'],     pil_font(14), PIL_DARK)
    img.save(output_path)
    print(f"  badge PNG: {output_path}")

# =========================================================
# PART 3: メイン生成（イラスト先行生成 → PDF埋め込み）
# =========================================================

def generate_all(slides_data, illustrations, output_dir, theme_name):
    os.makedirs(output_dir, exist_ok=True)
    safe = theme_name.replace('/', '_').replace('\\', '_').replace(' ', '_')

    print(f"\n出力先: {output_dir}")
    print("-" * 56)

    # Step1: イラストPNGを先に生成
    print("[1/2] イラストPNGを生成...")
    illust_paths = {}
    for illust in illustrations:
        t    = illust['type']
        path = os.path.join(output_dir, f"{safe}_{t}.png")
        if   t == 'step':       make_step_illust(illust, path)
        elif t == 'comparison': make_comparison_illust(illust, path)
        elif t == 'badge':      make_badge_illust(illust, path)
        illust_paths[t] = path

    # Step2: illust型スライドに画像パスを注入
    for slide in slides_data:
        if slide.get('type') == 'illust':
            slide['_img_path'] = illust_paths.get(slide.get('illust_type', ''), '')

    # Step3: PDF生成（全8枚・イラスト埋め込み済み）
    print("[2/2] スライドPDFを生成（イラスト埋め込み済み）...")
    generate_slides(slides_data, os.path.join(output_dir, f"{safe}_スライド.pdf"))

    print("-" * 56)
    print(f"完了！{1 + len(illustrations)} ファイルを出力しました。")

# =========================================================
# テーマデータ（Claude が生成する部分）
# =========================================================
THEME   = "{THEME_NAME}"
OUT_DIR = r"C:\Users\haiki\OneDrive\デスクトップ\スキル\スキル開発\スライド\output_{THEME_SAFE}"

slides = [
    # 1. テキスト
    {
        "type": "intro", "page": 1, "theme": THEME,
        "title": f"{THEME}とは？",
        "points": [
            {"label": "ポイント1", "tagline": "キャッチフレーズ",
             "bullets": ["詳細1", "詳細2", "詳細3", "詳細4"]},
            {"label": "ポイント2", "tagline": "キャッチフレーズ",
             "bullets": ["詳細1", "詳細2", "詳細3", "詳細4"]},
            {"label": "ポイント3", "tagline": "キャッチフレーズ",
             "bullets": ["詳細1", "詳細2", "詳細3", "詳細4"]},
        ]
    },
    # 2. テキスト
    {
        "type": "before", "page": 2, "theme": THEME,
        "title": f"{THEME}がない世界",
        "items": [
            {"label": "課題1", "desc": "概要説明",
             "points": ["問題点1","問題点2","問題点3","問題点4"]},
            {"label": "課題2", "desc": "概要説明",
             "points": ["問題点1","問題点2","問題点3","問題点4"]},
        ],
        "conclusion": "従来はこれが当たり前でした"
    },
    # 3. イラスト（comparison埋め込み）
    {
        "type": "illust", "page": 3, "theme": THEME,
        "title": f"{THEME}導入で何が変わる？",
        "illust_type": "comparison",
    },
    # 4. テキスト
    {
        "type": "bullets", "page": 4, "theme": THEME,
        "title": f"{THEME}の仕組み",
        "bullets": [
            {"title": "ポイント1", "desc": "説明文"},
            {"title": "ポイント2", "desc": "説明文"},
            {"title": "ポイント3", "desc": "説明文"},
            {"title": "ポイント4", "desc": "説明文"},
            {"title": "ポイント5", "desc": "説明文"},
        ],
        "conclusion": "難しそうに見えますが、心配無用です！"
    },
    # 5. イラスト（step埋め込み）
    {
        "type": "illust", "page": 5, "theme": THEME,
        "title": f"{THEME}の始め方",
        "illust_type": "step",
    },
    # 6. テキスト
    {
        "type": "categories", "page": 6, "theme": THEME,
        "title": f"{THEME}でできること：具体例",
        "categories": [
            {"name": "カテゴリA", "items": [
                {"name": "例1", "desc": "説明"},
                {"name": "例2", "desc": "説明"},
                {"name": "例3", "desc": "説明"},
            ]},
            {"name": "カテゴリB", "items": [
                {"name": "例1", "desc": "説明"},
                {"name": "例2", "desc": "説明"},
                {"name": "例3", "desc": "説明"},
            ]},
            {"name": "カテゴリC", "items": [
                {"name": "例1", "desc": "説明"},
                {"name": "例2", "desc": "説明"},
                {"name": "例3", "desc": "説明"},
            ]},
        ],
        "conclusion": "これらすべて、活用できます！"
    },
    # 7. テキスト
    {
        "type": "warnings", "page": 7, "theme": THEME,
        "title": "知っておきたい注意点",
        "items": [
            {"title": "注意点1", "desc": "詳細説明。リスクと対処法を3行以内で。"},
            {"title": "注意点2", "desc": "詳細説明。リスクと対処法を3行以内で。"},
            {"title": "注意点3", "desc": "詳細説明。リスクと対処法を3行以内で。"},
        ],
        "conclusion": "正しく知って、安全に活用しましょう！"
    },
    # 8. イラスト（badge埋め込み）
    {
        "type": "illust", "page": 8, "theme": THEME,
        "title": f"{THEME}で得られる3つの変化",
        "illust_type": "badge",
    },
]

illustrations = [
    {
        "type": "step",
        "title": f"{THEME}の始め方",
        "steps": [
            {"num": "①", "title": "ステップ1", "desc": "説明"},
            {"num": "②", "title": "ステップ2", "desc": "説明"},
            {"num": "③", "title": "ステップ3", "desc": "説明"},
            {"num": "④", "title": "ステップ4", "desc": "説明"},
        ]
    },
    {
        "type": "comparison",
        "before": {"label": "BEFORE", "items": ["問題1", "問題2", "問題3"]},
        "after":  {"label": f"{THEME}あり", "items": ["解決1", "解決2", "解決3"]},
    },
    {
        "type": "badge",
        "items": [
            {"icon": "★", "value": "〇〇倍", "label": "効果・数値"},
            {"icon": "★", "value": "〇〇個", "label": "効果・数値"},
            {"icon": "★", "value": "〇〇h",  "label": "効果・数値"},
        ]
    },
]

generate_all(slides, illustrations, OUT_DIR, THEME)
```

---

## Claudeの役割（スキル発動時）

### Step 1: ヒアリング（AskUserQuestionで2問）

**第1問：テーマと対象者**
```
「テーマと対象者を教えてください。
 例：「副業の始め方・会社員向け」「Notion活用法・初心者向け」」
```

**第2問：ページ数**
```
「スライドは何枚にしますか？
 ・3枚（ショート：紹介・比較・まとめ）
 ・5枚（標準：テキストのみ）
 ・6枚（バランス：テキスト＋比較イラスト1枚）
 ・8枚（フル・デフォルト：テキスト5枚＋イラスト3枚）
 ・カスタム（枚数を指定）」
```

ページ数が未指定・「デフォルト」・「おすすめ」の場合は **8枚** を採用する。

### Step 2: 全コンテンツを一括設計

ページ数に応じた構成で `slides` を設計する（上記「ページ数別テンプレート」参照）。

| ページ数 | slides構成 | illustrations |
|---------|-----------|--------------|
| 3枚 | intro → illust(comparison) → warnings | comparison のみ |
| 5枚 | intro → before → bullets → categories → warnings | なし |
| 6枚 | intro → before → illust(comparison) → bullets → categories → warnings | comparison のみ |
| 8枚 | intro → before → illust(comparison) → bullets → illust(step) → categories → warnings → illust(badge) | 全3種 |
| カスタム | テーマ・目的に合わせてClaudeが判断 | 必要に応じて |

**illust型スライドが含まれる場合、`illustrations` リストも同時に設計すること。**

上記テンプレートの `slides` と（必要であれば）`illustrations` を**同時に**テーマ内容で埋める。

**illust型スライドの`title`はイラストの内容に合わせて変更すること。**

**イラスト設計の指針:**
- `step`: テーマの「始め方・手順」を3〜4ステップで
- `comparison`: テーマ「なし」vs「あり」で変わる点を3項目ずつ
- `badge`: テーマの効果を表す数値・キーワードを3つ（例: 10倍・0円・24h）

### Step 3: スクリプトを書き出して実行

```
OUT_DIR = r"C:\Users\haiki\OneDrive\デスクトップ\スキル\スキル開発\スライド\output_{テーマ名}"
```

1. Writeツールでスクリプトをファイルに書き出し
2. Bashツールで実行（`python {ファイル名}.py`）
3. 生成されたファイル一覧をユーザーに報告

---

## 出力ファイル構成

```
output_{テーマ}/
  ├── {テーマ}_スライド.pdf   ← 統合スライド（ページ数に応じて3〜8枚）
  ├── {テーマ}_step.png       ← ステップ図（illust(step)使用時のみ）
  ├── {テーマ}_comparison.png ← Before/After比較（illust(comparison)使用時のみ）
  └── {テーマ}_badge.png      ← 数値バッジ（illust(badge)使用時のみ）
```

---

## 必要ライブラリ

```bash
pip install reportlab Pillow
```

---

*full-deck v2 — イラストをPDF内に統合した完全プレゼンテーション自動生成スキル*
