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
PIL_LIGHT  = (178, 235, 242)

# =========================================================
# フォント
# =========================================================
FONT_CANDIDATES = [
    ("C:/Windows/Fonts/meiryo.ttc",   "Meiryo"),
    ("C:/Windows/Fonts/msgothic.ttc", "MSGothic"),
    ("C:/Windows/Fonts/YuGothR.ttc",  "YuGothic"),
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

# ---------- slide_illust（PNG埋め込みスライド）----------
def slide_illust(c, data):
    """イラストPNGをスライド本文エリアに埋め込む"""
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
        # 薄いカード背景
        c.setFillColor(RL_WHITE)
        c.rect(SL_MARGIN, BODY_BOTTOM+pad//2,
               W_SL-SL_MARGIN*2, BODY_H-pad, fill=1, stroke=0)
        c.drawImage(img_path, dx, dy, dw, dh, preserveAspectRatio=True, mask='auto')
    c.showPage()

# ---------- テキストスライド群 ----------
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
        c.drawString(x+pad, cy+BODY_H-36, pt['label'])
        if pt.get('tagline'):
            c.setFillColor(RL_ACCENT); c.setFont(RL_FONT, 13)
            c.drawString(x+pad, cy+BODY_H-56, pt['tagline'])
        sl_divider(c, x+pad, cy+BODY_H-66, tw)
        by = cy+BODY_H-86
        for b in pt.get('bullets', []):
            if not b: continue
            lines = sl_wrap(b, RL_FONT, 13, tw-18)
            c.setFillColor(RL_ACCENT); c.setFont(RL_FONT_BOLD, 14); c.drawString(x+pad, by, "•")
            c.setFillColor(RL_TEXT);   c.setFont(RL_FONT, 13)
            for j, ln in enumerate(lines[:3]): c.drawString(x+pad+16, by-j*16, ln)
            by -= (16*min(len(lines),3))+12
            if by < cy+14: break
    c.showPage()

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
        c.drawString(x+pad+4, card_y+ch-28, item['label'])
        ty = card_y+ch-62
        sl_draw_wrapped(c, item['desc'], x+pad, ty, RL_FONT, 14, RL_TEXT, tw, ml=4)
        if item.get('points'):
            sl_divider(c, x+pad, ty-76, tw)
            py = ty-94
            for pt_text in item['points']:
                lns = sl_wrap(pt_text, RL_FONT, 13, tw-18)
                c.setFillColor(RL_ACCENT); c.setFont(RL_FONT_BOLD, 14); c.drawString(x+pad, py, "›")
                c.setFillColor(RL_TEXT); c.setFont(RL_FONT, 13)
                for j, ln in enumerate(lns[:2]): c.drawString(x+pad+14, py-j*16, ln)
                py -= (16*min(len(lns),2))+10
                if py < card_y+10: break
    if data.get('conclusion'):
        c.setFillColor(RL_ACCENT); c.rect(SL_MARGIN, BODY_BOTTOM, W_SL-SL_MARGIN*2, concl_h, fill=1, stroke=0)
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, 15)
        c.drawCentredString(W_SL/2, BODY_BOTTOM+12, data['conclusion'])
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
    box_w = min(190, (W-60)//(n) - 10)
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
        # 番号バッジ
        cx_b = bx+box_w//2
        d.ellipse([cx_b-22, by+10, cx_b+22, by+54], fill=PIL_ORANGE)
        pil_text_c(d, cx_b, by+32, step['num'], pil_font(18), PIL_WHITE)
        # タイトル
        pil_text_c(d, cx_b, by+72, step.get('title',''), pil_font(15), PIL_TEAL)
        # 説明
        pil_multiline_c(d, cx_b, by+95, step.get('desc',''), pil_font(12), PIL_DARK, lh=17)
        # 矢印
        if i < n-1:
            arr_x = bx+box_w+4
            arr_y = H//2 + (8 if data.get('title') else 0)
            pil_arrow_right(d, arr_x, arr_y, gap-8, PIL_TEAL, th=5)

    img.save(output_path)
    print(f"  step PNG: {output_path}")

def make_comparison_illust(data, output_path):
    W, H  = 900, 340
    img   = Image.new('RGB', (W,H), PIL_BG)
    d     = ImageDraw.Draw(img)
    pad   = 36
    pw    = (W-pad*3)//2
    ph    = H-pad*2

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
# PART 3: 一括生成（イラスト生成 → PDF埋め込み）
# =========================================================

def generate_all(slides_data, illustrations, output_dir, theme_name):
    os.makedirs(output_dir, exist_ok=True)
    safe = theme_name.replace('/', '_').replace('\\', '_').replace(' ', '_')

    # Step1: イラストPNGを先に生成
    print(f"\n出力先: {output_dir}")
    print("-" * 56)
    print("[1/2] イラストPNGを生成...")
    illust_paths = {}
    for illust in illustrations:
        t    = illust['type']
        path = os.path.join(output_dir, f"{safe}_{t}.png")
        if   t == 'step':       make_step_illust(illust, path)
        elif t == 'comparison': make_comparison_illust(illust, path)
        elif t == 'badge':      make_badge_illust(illust, path)
        illust_paths[t] = path

    # Step2: イラストスライドのパスを注入
    for slide in slides_data:
        if slide.get('type') == 'illust':
            slide['_img_path'] = illust_paths.get(slide.get('illust_type', ''), '')

    # Step3: PDF生成（テキストスライド＋イラストスライドを一本化）
    print("[2/2] スライドPDFを生成（イラスト埋め込み済み）...")
    generate_slides(slides_data, os.path.join(output_dir, f"{safe}_スライド.pdf"))

    print("-" * 56)
    total_files = 1 + len(illustrations)
    print(f"完了！{total_files}ファイルを出力しました。")
    print(f"  {safe}_スライド.pdf  ← {len(slides_data)}枚（テキスト＋イラスト統合）")
    for t, p in illust_paths.items():
        print(f"  {os.path.basename(p)}")

# =========================================================
# スライドデータ（8枚：テキスト5 ＋ イラスト3）
# =========================================================
THEME = "Python入門（プログラミング初心者向け）"

slides = [
    # --- 1. テキスト: Pythonとは？ ---
    {
        "type": "intro", "page": 1, "theme": THEME,
        "title": "Pythonとは？",
        "points": [
            {
                "label": "誰でも書けるシンプルな言語",
                "tagline": "英語に近い読みやすい文法",
                "bullets": [
                    "コードが短く直感的にわかりやすい",
                    "プログラミング経験ゼロでも始められる",
                    "世界中で使われている人気No.1言語",
                    "日本語の解説サイト・動画が豊富",
                ]
            },
            {
                "label": "何でも作れる万能ツール",
                "tagline": "1つ覚えれば幅広く活用できる",
                "bullets": [
                    "Webアプリ・業務ツールが作れる",
                    "データ分析・AI開発にも使える",
                    "Excelの自動化で仕事が一気に楽に",
                    "無料で使えるライブラリが豊富",
                ]
            },
            {
                "label": "今すぐ始められる",
                "tagline": "準備ゼロ・費用ゼロでスタート",
                "bullets": [
                    "インストール5分で環境構築完了",
                    "Google Colabならブラウザだけで動く",
                    "完全無料で使い続けられる",
                    "挫折しにくい学習コミュニティが豊富",
                ]
            },
        ]
    },
    # --- 2. テキスト: Pythonがない世界 ---
    {
        "type": "before", "page": 2, "theme": THEME,
        "title": "Pythonがない世界",
        "items": [
            {
                "label": "繰り返し作業を毎日手動でこなす",
                "desc": "ExcelやWordの作業を毎日手作業で繰り返し、膨大な時間を消費してしまう。",
                "points": [
                    "同じコピー&ペーストを何百回も繰り返す",
                    "ファイルの名前変更を1つずつ手動で行う",
                    "集計ミスが頻発し修正に何時間も取られる",
                    "自動化する方法を知らず諦め続けてしまう",
                ]
            },
            {
                "label": "データを活かせず判断が遅くなる",
                "desc": "大量データを前に何も分析できず、感覚と経験だけで意思決定してしまう。",
                "points": [
                    "Excelで限界を感じてもその先に進めない",
                    "グラフを作るだけで何時間もかかる",
                    "データから傾向を読み取る術を知らない",
                    "AIを活用したいが何から始めるかわからない",
                ]
            },
        ],
        "conclusion": "これが「Pythonを知らない」状態のリアルです"
    },
    # --- 3. イラスト: Before/After 比較図 ---
    {
        "type": "illust", "page": 3, "theme": THEME,
        "title": "Python導入で何が変わる？",
        "illust_type": "comparison",
    },
    # --- 4. テキスト: Pythonの仕組み ---
    {
        "type": "bullets", "page": 4, "theme": THEME,
        "title": "Pythonの仕組み：5つのキー概念",
        "bullets": [
            {"title": "インタープリタ言語",
             "desc": "コードを1行ずつ読みながら即実行。書いてすぐ結果が確認できるので初心者に最適。"},
            {"title": "ライブラリ",
             "desc": "先人が作った便利な機能集。importするだけで複雑な処理も数行で書ける。"},
            {"title": "変数とデータ型",
             "desc": "数値・文字・リストなど情報を名前付きの箱に入れて管理するプログラムの基本。"},
            {"title": "関数",
             "desc": "繰り返し使う処理を1つにまとめる仕組み。コードが短くなり読みやすくなる。"},
            {"title": "if文・ループ",
             "desc": "条件に応じて動きを変えたり、同じ処理を繰り返す制御構文の基本中の基本。"},
        ],
        "conclusion": "この5つを理解するだけで、できることが爆発的に広がります！"
    },
    # --- 5. イラスト: 始め方ステップ図 ---
    {
        "type": "illust", "page": 5, "theme": THEME,
        "title": "Pythonの始め方・4ステップ",
        "illust_type": "step",
    },
    # --- 6. テキスト: Pythonでできること ---
    {
        "type": "categories", "page": 6, "theme": THEME,
        "title": "Pythonでできること：具体例",
        "categories": [
            {
                "name": "仕事効率化",
                "items": [
                    {"name": "Excelの自動処理", "desc": "毎日のルーティン作業を完全自動化できる"},
                    {"name": "メール一括送信", "desc": "宛先・本文を変えながら大量メールを数秒で送れる"},
                    {"name": "PDF変換・結合", "desc": "複数ファイルを瞬時に変換・まとめて管理できる"},
                ]
            },
            {
                "name": "データ分析・AI",
                "items": [
                    {"name": "グラフ作成", "desc": "美しいグラフを数行のコードで描ける"},
                    {"name": "機械学習", "desc": "scikit-learnで予測モデルを数十行で作れる"},
                    {"name": "データ集計", "desc": "pandasで大量データを瞬時に加工・集計できる"},
                ]
            },
            {
                "name": "Web・アプリ開発",
                "items": [
                    {"name": "スクレイピング", "desc": "Webサイトの情報を自動収集・データ化できる"},
                    {"name": "Webアプリ", "desc": "FlaskやDjangoで本格的なWebサイトを作れる"},
                    {"name": "LINE Bot", "desc": "自動返信するBotを無料で作成できる"},
                ]
            },
        ],
        "conclusion": "全部Pythonひとつでできます！"
    },
    # --- 7. テキスト: 注意点 ---
    {
        "type": "warnings", "page": 7, "theme": THEME,
        "title": "知っておきたい「3つの注意点」",
        "items": [
            {
                "title": "エラーは「ヒント」、失敗ではない",
                "desc": "Pythonは必ずエラーを出します。メッセージをコピーして検索するのが上達の近道。「エラー＝失敗」ではなく「次にやることを教えてくれるヒント」と捉えましょう。"
            },
            {
                "title": "写経だけでは応用力が育たない",
                "desc": "教材コードをそのまま写すだけでは実践力が育ちません。「自分が作りたいもの」を小さく決めて実際に手を動かすことが一番の上達法です。"
            },
            {
                "title": "Python3系を使うこと（2系は非推奨）",
                "desc": "PythonにはPython2とPython3があります。現在の標準はPython3です。古い記事のコードはPython2の場合があるので、必ずバージョンを確認しましょう。"
            },
        ],
        "conclusion": "エラーを恐れず、小さく作り始めましょう！"
    },
    # --- 8. イラスト: まとめバッジ ---
    {
        "type": "illust", "page": 8, "theme": THEME,
        "title": "Pythonで得られる3つの変化",
        "illust_type": "badge",
    },
]

# =========================================================
# イラストデータ
# =========================================================
illustrations = [
    {
        "type": "step",
        "title": "Pythonの始め方・4ステップ",
        "steps": [
            {"num": "①", "title": "インストール",    "desc": "公式サイトから\n無料でダウンロード\n（約5分）"},
            {"num": "②", "title": "Hello World",     "desc": "print('Hello!')\nを実行して\n動作確認"},
            {"num": "③", "title": "小さなツール作り", "desc": "興味ある課題を\n解決する小さな\nプログラムを作る"},
            {"num": "④", "title": "ライブラリ活用",  "desc": "pipでインストール\nして機能を\n拡張していく"},
        ]
    },
    {
        "type": "comparison",
        "before": {
            "label": "Python なし",
            "items": ["毎日手作業で消耗", "データ分析できない", "自動化は夢のまた夢"]
        },
        "after": {
            "label": "Python あり",
            "items": ["面倒な作業を自動化", "データを即可視化", "アイデアをすぐ形に"]
        },
    },
    {
        "type": "badge",
        "items": [
            {"icon": "⏱", "value": "30分",  "label": "環境構築時間"},
            {"icon": "💡", "value": "3行",   "label": "Hello World"},
            {"icon": "★",  "value": "1位",   "label": "人気言語ランキング"},
        ]
    },
]

OUT_DIR = r"C:\Users\haiki\OneDrive\デスクトップ\スキル\スキル開発\スライド\output_Python入門v2"
generate_all(slides, illustrations, OUT_DIR, "Python入門")
