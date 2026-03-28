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
# カラー定数
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
    ("C:/Windows/Fonts/meiryo.ttc",   "Meiryo"),
    ("C:/Windows/Fonts/msgothic.ttc", "MSGothic"),
    ("C:/Windows/Fonts/YuGothR.ttc",  "YuGothic"),
    ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", "HiraginoKaku"),
]
FONT_PATH = next((p for p, _ in FONT_CANDIDATES if os.path.exists(p)), None)

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
# PART 1: スライド描画
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
    c.showPage()

def slide_illust(c, data):
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
        c.setFillColor(RL_WHITE)
        c.rect(SL_MARGIN, BODY_BOTTOM+pad//2,
               W_SL-SL_MARGIN*2, BODY_H-pad, fill=1, stroke=0)
        c.drawImage(img_path, dx, dy, dw, dh,
                    preserveAspectRatio=True, mask='auto')
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
    c.showPage()

def generate_slides(slides_data, output_path):
    c = canvas.Canvas(output_path, pagesize=(W_SL, H_SL))
    total = len(slides_data)
    for slide in slides_data:
        slide['total'] = total
        t = slide.get('type')
        if   t == 'intro':    slide_intro(c, slide)
        elif t == 'illust':   slide_illust(c, slide)
        elif t == 'warnings': slide_warnings(c, slide)
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

# =========================================================
# PART 3: メイン生成
# =========================================================
def generate_all(slides_data, illustrations, output_dir, theme_name):
    os.makedirs(output_dir, exist_ok=True)
    safe = theme_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
    print(f"\n出力先: {output_dir}")
    print("-" * 56)
    print("[1/2] イラストPNGを生成...")
    illust_paths = {}
    for illust in illustrations:
        t    = illust['type']
        path = os.path.join(output_dir, f"{safe}_{t}.png")
        if t == 'comparison': make_comparison_illust(illust, path)
        illust_paths[t] = path
    for slide in slides_data:
        if slide.get('type') == 'illust':
            slide['_img_path'] = illust_paths.get(slide.get('illust_type', ''), '')
    print("[2/2] スライドPDFを生成（イラスト埋め込み済み）...")
    generate_slides(slides_data, os.path.join(output_dir, f"{safe}_スライド.pdf"))
    print("-" * 56)
    print(f"完了！{1 + len(illustrations)} ファイルを出力しました。")

# =========================================================
# テーマデータ
# =========================================================
THEME   = "節約術・一人暮らし向け"
OUT_DIR = r"C:\Users\haiki\OneDrive\デスクトップ\スキル\スキル開発\スライド\output_節約術"

slides = [
    # 1. intro
    {
        "type": "intro", "page": 1, "theme": THEME,
        "title": "節約術とは？一人暮らしの賢いお金管理",
        "points": [
            {
                "label": "食費を減らす",
                "tagline": "自炊・まとめ買い・冷凍活用",
                "bullets": [
                    "週1まとめ買いで衝動買いを防ぐ",
                    "冷凍保存で食材を無駄にしない",
                    "自炊1食200円以内を目指す",
                    "コンビニ頼りをやめるだけで月1万円節約",
                ]
            },
            {
                "label": "固定費を見直す",
                "tagline": "スマホ・保険・サブスク",
                "bullets": [
                    "格安SIMで月5,000円削減",
                    "不要なサブスクを全解約",
                    "保険の見直しで年1〜3万円節約",
                    "電気・ガスのプランを比較検討",
                ]
            },
            {
                "label": "貯金を習慣化する",
                "tagline": "先取り貯金が最強ルール",
                "bullets": [
                    "給料日に即座に先取り貯金",
                    "財布の現金は週の予算だけ",
                    "小さな目標（3ヶ月3万円）で達成感",
                    "家計簿アプリで支出を見える化",
                ]
            },
        ]
    },
    # 2. illust（comparison埋め込み）
    {
        "type": "illust", "page": 2, "theme": THEME,
        "title": "節約前 vs 節約後：こんなに変わる！",
        "illust_type": "comparison",
    },
    # 3. warnings
    {
        "type": "warnings", "page": 3, "theme": THEME,
        "title": "知っておきたい注意点",
        "items": [
            {
                "title": "やりすぎると続かない",
                "desc": "食費を極端に削ると栄養不足・ストレスの原因に。週1〜2回は好きなものを食べる日を作り、無理なく続けられる範囲でコントロールしよう。"
            },
            {
                "title": "固定費の見直しは慎重に",
                "desc": "スマホや保険の変更は保障内容が薄くなる場合がある。料金だけで判断せず、必要なカバレッジを確認してからプランを変更すること。"
            },
            {
                "title": "節約したお金の使い道を決める",
                "desc": "浮いたお金を貯金・投資・スキルアップに回すことで将来の安心につながる。目的なき節約はモチベーションが続かないので、ゴールを明確にしよう。"
            },
        ],
        "conclusion": "無理せず・賢く・楽しく節約を続けましょう！"
    },
]

illustrations = [
    {
        "type": "comparison",
        "before": {
            "label": "節約なし",
            "items": ["月収の30%が食費に消える", "不要なサブスク5件以上", "毎月赤字・貯金ゼロ"]
        },
        "after": {
            "label": "節約術あり",
            "items": ["食費を月2万円以内に削減", "固定費が月1万円以上ダウン", "毎月3〜5万円の貯金が貯まる"]
        },
    },
]

generate_all(slides, illustrations, OUT_DIR, THEME)
