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

def slide_illust(c, data):
    sl_bg(c); sl_header(c, data['title']); sl_footer(c, data['page'], data['total'], data['theme'])
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
        c.rect(SL_MARGIN, BODY_BOTTOM+pad//2, W_SL-SL_MARGIN*2, BODY_H-pad, fill=1, stroke=0)
        c.drawImage(img_path, dx, dy, dw, dh, preserveAspectRatio=True, mask='auto')
    c.showPage()

# ---- スライド1: 動的スロット配置でbulletsを均等分散 ----
def slide_intro(c, data):
    sl_bg(c); sl_header(c, data['title']); sl_footer(c, data['page'], data['total'], data['theme'])
    GAP, pad = 14, 16
    col_w = (W_SL - SL_MARGIN*2 - GAP*2) // 3
    tw    = col_w - pad*2
    for i, pt in enumerate(data['points'][:3]):
        x = SL_MARGIN + i*(col_w+GAP); cy = BODY_BOTTOM
        sl_card(c, x, cy, col_w, BODY_H)
        # 上部アクセントバー
        c.setFillColor(RL_ACCENT); c.rect(x, cy+BODY_H-8, col_w, 8, fill=1, stroke=0)
        # ラベル
        c.setFillColor(RL_HEADER); c.setFont(RL_FONT_BOLD, 20)
        c.drawString(x+pad, cy+BODY_H-34, pt['label'])
        # タグライン
        if pt.get('tagline'):
            c.setFillColor(RL_ACCENT); c.setFont(RL_FONT, 13)
            c.drawString(x+pad, cy+BODY_H-54, pt['tagline'])
        # 区切り線
        sl_divider(c, x+pad, cy+BODY_H-64, tw)

        # ====== 動的スロット: 利用可能な高さを箇条書き数で均等分割 ======
        bullets_list = [b for b in pt.get('bullets', []) if b]
        n_b = len(bullets_list)
        if n_b > 0:
            area_top    = cy + BODY_H - 72  # 区切り線の少し下
            area_bottom = cy + 16           # カード下部パディング
            slot_h      = (area_top - area_bottom) // n_b
            for idx, b in enumerate(bullets_list):
                # 各スロットの中央上部にテキストを配置
                slot_top = area_top - slot_h * idx
                by       = slot_top - max(6, (slot_h - 20) // 2)
                lines    = sl_wrap(b, RL_FONT, 14, tw-20)
                c.setFillColor(RL_ACCENT); c.setFont(RL_FONT_BOLD, 16)
                c.drawString(x+pad, by, "•")
                c.setFillColor(RL_TEXT); c.setFont(RL_FONT, 14)
                for j, ln in enumerate(lines[:2]):
                    c.drawString(x+pad+18, by-j*18, ln)
    c.showPage()

# ---- スライド2: 動的スロット配置でpointsを均等分散 ----
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
        # ヘッダーバー
        c.setFillColor(RL_HEADER); c.rect(x, card_y+ch-40, col_w, 40, fill=1, stroke=0)
        c.setFillColor(RL_ACCENT); c.rect(x, card_y+ch-40, 6, 40, fill=1, stroke=0)
        lsz = 17 if stringWidth(item['label'], RL_FONT_BOLD, 17) <= tw-10 else 14
        c.setFillColor(RL_WHITE); c.setFont(RL_FONT_BOLD, lsz)
        c.drawString(x+pad+4, card_y+ch-26, item['label'])
        # 概要説明文
        ty = card_y+ch-58
        desc_end = sl_draw_wrapped(c, item['desc'], x+pad, ty, RL_FONT, 14, RL_TEXT, tw, ml=3)
        # 区切り線（説明文終端の14px下）
        div_y = desc_end - 14
        sl_divider(c, x+pad, div_y, tw)

        # ====== 動的スロット: 区切り線〜カード下部を均等分割 ======
        if item.get('points'):
            pts_top    = div_y - 14  # 区切り線から14px下
            pts_bottom = card_y + 12
            points_list = item['points']
            n_p     = len(points_list)
            slot_p  = (pts_top - pts_bottom) // max(n_p, 1)
            for idx, pt_text in enumerate(points_list):
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
# PART 3: 一括生成
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
        if   t == 'step':       make_step_illust(illust, path)
        elif t == 'comparison': make_comparison_illust(illust, path)
        elif t == 'badge':      make_badge_illust(illust, path)
        illust_paths[t] = path
    for slide in slides_data:
        if slide.get('type') == 'illust':
            slide['_img_path'] = illust_paths.get(slide.get('illust_type', ''), '')
    print("[2/2] スライドPDFを生成（イラスト埋め込み済み）...")
    generate_slides(slides_data, os.path.join(output_dir, f"{safe}_スライド.pdf"))
    print("-" * 56)
    print(f"完了！{1 + len(illustrations)} ファイルを出力しました。")

# =========================================================
# スライドデータ
# =========================================================
THEME = "副業の始め方（会社員向け）"

slides = [
    {
        "type": "intro", "page": 1, "theme": THEME,
        "title": "副業とは？なぜ今必要か",
        "points": [
            {
                "label": "給与以外の収入を作る手段",
                "tagline": "本業を続けながら収入を増やす方法",
                "bullets": [
                    "月数千円から始められる低リスク",
                    "好きなこと・スキルを活かせる",
                    "本業経験や知識をそのまま活用できる",
                    "税金の仕組みを学ぶ入口にもなる",
                ]
            },
            {
                "label": "副業の種類は多様",
                "tagline": "あなたに合ったスタイルが必ずある",
                "bullets": [
                    "在宅でできる仕事（ライティング・デザイン）",
                    "スキルを売る（プログラミング・翻訳）",
                    "モノを売る（フリマ・ハンドメイド）",
                    "情報発信（ブログ・YouTube・SNS）",
                ]
            },
            {
                "label": "副業は未来への投資",
                "tagline": "収入＋スキル＋人脈が同時に育つ",
                "bullets": [
                    "本業リスクに備えた収入の複線化",
                    "自分の市場価値が上がる",
                    "副業から独立・起業へ発展する可能性",
                    "社外のリアルなビジネス経験が積める",
                ]
            },
        ]
    },
    {
        "type": "before", "page": 2, "theme": THEME,
        "title": "副業がない世界",
        "items": [
            {
                "label": "収入が会社に依存しきっている",
                "desc": "給与だけが唯一の収入源。会社の業績や景気に生活全体が左右される不安定な状態。",
                "points": [
                    "毎月の給与振込を待つだけの受動的な収入",
                    "リストラ・減給リスクを常に抱えている",
                    "昇給ペースが生活費の上昇に追いつかない",
                    "節約が唯一の選択肢になってしまう",
                ]
            },
            {
                "label": "スキルと時間が眠ったまま",
                "desc": "持っている専門知識や空き時間が活用されず、本業以外に価値を生み出せていない。",
                "points": [
                    "残業以外で収入を増やす手段を知らない",
                    "休日の時間を収益に変える発想がない",
                    "会社でしか通用しないスキルしか育たない",
                    "定年後や転職時の収入に漠然とした不安",
                ]
            },
        ],
        "conclusion": "これが「副業を知らない」会社員のリアルです"
    },
    {
        "type": "illust", "page": 3, "theme": THEME,
        "title": "副業導入で何が変わる？",
        "illust_type": "comparison",
    },
    {
        "type": "bullets", "page": 4, "theme": THEME,
        "title": "副業を成功させる5つのポイント",
        "bullets": [
            {"title": "仕組みを理解する",
             "desc": "副業は「労働収入」から「仕組み収入」へ移行するステップ。小さく始め、徐々に自動化できる。"},
            {"title": "スキルの棚卸しをする",
             "desc": "今持っているスキルや知識がそのまま商品になる。まず自分の強みリストを作ることから始めよう。"},
            {"title": "最初の1円を稼ぐ",
             "desc": "完璧を目指さず「最初の1円」を稼ぐことが最大の壁であり突破口。小さく行動が大切。"},
            {"title": "継続の仕組みを作る",
             "desc": "習慣化とスケジューリングが副業を長続きさせる唯一の方法。週2〜3時間から始めよう。"},
            {"title": "確定申告を先に理解する",
             "desc": "副業収入が年20万円を超えると確定申告が必要。住民税の処理方法も事前に把握しておこう。"},
        ],
        "conclusion": "この5つを押さえるだけで副業成功率が大きく変わります！"
    },
    {
        "type": "illust", "page": 5, "theme": THEME,
        "title": "副業の始め方・4ステップ",
        "illust_type": "step",
    },
    {
        "type": "categories", "page": 6, "theme": THEME,
        "title": "副業でできること：具体例",
        "categories": [
            {
                "name": "スキル系",
                "items": [
                    {"name": "Webライティング", "desc": "ブログや企業サイトの記事を執筆して報酬を得る"},
                    {"name": "デザイン（Canva）", "desc": "SNS投稿・バナーをデザインしてクラウドソーシングで受注"},
                    {"name": "動画編集", "desc": "YouTubeや企業動画の編集を在宅で請け負う"},
                ]
            },
            {
                "name": "物販・コンテンツ系",
                "items": [
                    {"name": "フリマ出品", "desc": "メルカリ・ラクマで不用品・せどりで収益化"},
                    {"name": "note・電子書籍", "desc": "知識・体験を文章にして販売。資産として収入が続く"},
                    {"name": "ハンドメイド販売", "desc": "自作品をminneやCreemaで販売できる"},
                ]
            },
            {
                "name": "情報発信系",
                "items": [
                    {"name": "ブログ・アフィリエイト", "desc": "記事が資産になり、寝ている間にも収益が発生"},
                    {"name": "YouTube", "desc": "専門知識を動画で発信して広告収入を得る"},
                    {"name": "SNS運用代行", "desc": "X・Instagram運用を企業から月額で受注できる"},
                ]
            },
        ],
        "conclusion": "本業のスキルと掛け合わせることで差別化できます！"
    },
    {
        "type": "warnings", "page": 7, "theme": THEME,
        "title": "知っておきたい「3つの注意点」",
        "items": [
            {
                "title": "就業規則の確認が最優先",
                "desc": "副業を始める前に会社の就業規則を必ず確認しましょう。副業禁止の場合は懲戒処分になる可能性があります。公務員は法律上副業が制限されています。"
            },
            {
                "title": "確定申告と住民税に要注意",
                "desc": "副業収入が年20万円超えで確定申告が必要です。住民税が増え会社にばれるケースもあるため、住民税の納付は「普通徴収」に設定しましょう。"
            },
            {
                "title": "本業パフォーマンスを落とさない",
                "desc": "副業に熱中しすぎて本業に影響が出ると本末転倒です。まずは週末や隙間時間だけで試す「低稼働スタート」がおすすめです。"
            },
        ],
        "conclusion": "ルールを守り、小さく始めることが長続きのコツです！"
    },
    {
        "type": "illust", "page": 8, "theme": THEME,
        "title": "副業で得られる3つの変化",
        "illust_type": "badge",
    },
]

illustrations = [
    {
        "type": "step",
        "title": "副業の始め方・4ステップ",
        "steps": [
            {"num": "①", "title": "スキル棚卸し",      "desc": "本業経験・趣味を\nリスト化して\n商品を決める"},
            {"num": "②", "title": "プラットフォーム登録", "desc": "ランサーズ・メルカリ\nなど無料で\n今すぐ登録できる"},
            {"num": "③", "title": "最初の1件を受注",   "desc": "完璧よりスピード優先\n最初の1円を\n稼ぐことが突破口"},
            {"num": "④", "title": "改善・単価アップ",   "desc": "実績を積んで\n単価を上げ\n収入を安定させる"},
        ]
    },
    {
        "type": "comparison",
        "before": {
            "label": "副業なし",
            "items": ["収入は会社頼み一本", "スキルが職場以外で活きない", "将来への漠然とした不安"]
        },
        "after": {
            "label": "副業あり",
            "items": ["毎月+αの安定副収入", "スキルが市場価値に変わる", "選択肢と自信が生まれる"]
        },
    },
    {
        "type": "badge",
        "items": [
            {"icon": "★", "value": "+月3万",  "label": "平均副収入"},
            {"icon": "★", "value": "2〜3h",  "label": "1日の作業時間"},
            {"icon": "★", "value": "0円",    "label": "始める初期費用"},
        ]
    },
]

OUT_DIR = r"C:\Users\haiki\OneDrive\デスクトップ\スキル\スキル開発\スライド\output_副業の始め方v2"
generate_all(slides, illustrations, OUT_DIR, "副業の始め方")
