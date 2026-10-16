#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feis-design-card —— 东方编辑刊物风卡片渲染器

H5 排版（HTML/CSS）→ macOS 原生 WebKit 离屏截图 → PNG。零安装。

用法：
    python3 render.py <manifest.json>

manifest 顶层字段：
    output_dir   str   必填，PNG 输出目录（绝对路径）
    canvas       [w,h] 可选，默认 [1080,1440]（3:4）
    display_font str   可选，标题/大字号展示字体 ttf（默认取技能自带得意黑）
    brand        dict  可选，品牌块：
        name        str  品牌名，默认 "非叔Design"
        logo        str  品牌标 PNG 绝对路径（白底黑字，脚本 logo.swift 产出）
        logo_h      int  品牌标显示高度 px，默认 46
        copyright   str  报尾版权行，默认 "Copyright © 2026 ｜ 非叔Design"。
                         含 "｜" 时自动拆两段：左边是版权声明、右边是品牌名。
                         **两段同色 #1A1A1A**，只靠字重分层（声明 400 / 品牌名 600）
    nav          list  可选，顶部四栏导航，默认见 DEFAULT_NAV。
                       每栏**一个单词**、不要方括号，右对齐靠字距撑开
    footer_left  str   可选，页脚左栏
    footer_right str   可选，页脚右栏
    cards        list  必填，卡片清单，每张卡字段：
        no          str   编号（仅记录用，**不再自动渲染**；要显示就显式写 meta_left）
        meta_left   str   元信息行左栏（如 "// 提示词解析 · 视觉逻辑"）
        meta_right  str   元信息行右栏（顶层 meta_right 的覆盖值）
        rule        bool  报头下方是否画细线（封面卡常用 true）
        title       list  大标题行，每行可带反白高亮：
                          ["先规定怎么思考", {"text":"再描述画什么","hl":"怎么思考"}]
        latin       str   超大拉丁字（如 "EDITORIAL"）
        latin_size  int   覆盖拉丁字号
        title_size  int   覆盖中文标题字号
        icon        str   章节图标（emoji）。**默认固定 🧩，一般不用写**；
                          只有整组卡要换主题符号时才显式覆盖
        heading     str   章节标题（如 "#碎碎念"）
        subtitle    str   章节副题（28px 浅灰），**按体裁判定二选一**：
                            文章讲步骤/流程 → "Step<整组全局序号> <短句>"，如 "Step1 留白要坚定"
                            文章是并列观点   → "<短句>"（不带序号），     如 "先讲清画面怎么工作"
                          **不写 * 号**（已废弃，非叔否掉）；封面卡不写。
                          N 从 1 起跨卡累加，不按卡号算、不每张重置。
                          heading 与 subtitle 都没写时，章节块整块不渲染
        paras       list  正文段落。每段两种写法：
                             "字符串"                       → 常规段
                             {"text":..,"size":22,"lead":1.55,"color":"#3A3A3A"}
                                                             → 该段单独覆盖字号/行高/墨色
                          英文提示词这类长外文用 size 22 收进一张卡；
                          **中文正文一律不写 size**（30px 是默认档）
        para_size   int   整卡覆盖正文字号（默认 30）。**只给「提示词卡」这类长文附录用**：
                          一整条生图提示词（约 1000 字）靠它收进一张卡。
                          常规论点卡一律不写
        ⚠ **全组字号只有两档，不许按卡微调**（2026-09-21 非叔否掉「每卡反推字号」）：
             中文叙述       30px  #1D1D1D   （默认值，不写 size）
             英文提示词/参数 22px  #3A3A3A   （写 {"size":22,"lead":1.55,"color":"#3A3A3A"}）
          同一档在**全组所有卡上用同一个数**。「这张字多就缩到 21、那张字少就放到 23」
          会让整组卡片看起来像草稿——长文请改拆卡，不要动字号。
          唯一的例外是无图卡：改用 list 条目／quote 金句撑版面，**不是**放大正文
        para_lead   float 整卡覆盖正文行高（默认 1.7），配 para_size 一起用
        layout      str   正文卡的**图文构图**，默认 "stack"（老行为，图在正文下方通栏）：
                             stack   纵向堆叠（默认，老 manifest 不写即此项）
                             inline  嵌入式——图插在段落之间，通栏；过高则限高居中
                             side    左右构图——图在一侧、正文在另一侧
                             auto    按首图比例自动选：竖图(<0.95)→side，其余→inline
                          ⚠ **inline / side 绝不裁图**——图是这一页的主要内容时用它们。
                             老 stack 模式仍会为凑高度而裁，封面出血除外。
        side        str   side 模式里图放哪一侧："left"（默认）/ "right"
        side_w      float side 模式图占版心宽的比例上限，默认 0.62
        side_fill   float side 模式图高占可用高度的比例上限，默认 0.92
                          （两个默认值是量出来的：图占满可用高度大半，只留约 100px
                            呼吸，同时文字栏还剩约 318px，中文约 12 字/行仍可读）
        valign      str  版心纵向排布（组级或卡级）：
                            "fixed"   **新卡组默认**。顶隙（报头→标题）固定为
                                      top_gap(84)，**每页完全一致**；内容从标题
                                      顺排向下，余量留在底部（底隙随内容浮动）。
                                      2026-09-23 非叔：「保持不了二者一致，至少
                                      保证每页标题和页眉之间距离一样——读者都是
                                      从上至下看的」。
                            "center"  老版上下对称：顶隙 = 底隙，但顶隙会随内容
                                      高度浮动，翻组时标题上下跳，**新卡组不要用**
                            "top"     老行为（默认）：内容从顶部排到底，余量被图
                                      吃掉，底部贴报尾、顶部松，头重脚轻
                          fixed 模式下 .hd 的 60px 上边距自动归零，顶隙由
                          padding-top 独占；图/清单/金句一律不再吃剩余空间。
                          ⚠ **图必须与正文等宽 952**：方图走 stack + height(≈440)
                          + pos 通栏横窗；别给 inline 图写小 height，那会缩成窄图、
                          右侧留一大块空白
        top_gap     int   valign:"fixed" 时的顶隙像素，默认 84（常量 TOP_GAP）。
                          全组写同一个数，不要按卡调
        image_at    int   inline 模式下图插在第几段之后（默认 1 = 首段之后；0 = 全段之前）
        list        list  **无图卡的正文替身（首选）**。原文某个章节没配图时，用
                          「细线分隔的条目行」把版面撑满——绝不许拿一个**没有含义的大字**
                          糊过去（2026-09-21 非叔否掉：「不能因为没图片就不写了」）。
                          每行两种写法：
                             "圆领袍 · 幞头 · 革带 · 鱼袋"             → 单栏文字行
                             {"k":"形制","v":"圆领袍 · 幞头 · 革带"}   → 左小标签 + 右正文
                          行高可被撑开吸收剩余空间（每行上限 160px），所以整页从标题一路
                          走到报尾，底部不留空洞。**条目必须是文章自己的信息**
                          （形制/场景/光线/比例/负面词），不许为了填空编凑
        quote       str|dict 无图卡的「金句块」，可与 list 并用。把原文里最有态度的一句
                          放到配图本该在的位置，用超大字撑起版面（默认 68px 得意黑 #0D0D0D）：
                             {"text":"衣冠治国\n盛世礼序","size":72,"by":"唐制 · 圆领袍"}
                          文字**必须摘自原文**，不许自造口号
        giant       str|dict  **不推荐，仅为兼容旧 manifest 保留**。用无意义的超大单字
                          「占位」会在页面中央留出一大片灰白空洞，看着像没写完；
                          新卡请改用 list / quote。尺寸语义同旧版：
                             {"text":"唐","height":534,"size":380,"color":"#EDEDED"}
        images      list  配图：[{"path":..,"caption":..,"pos":..,"bleed":true,"height":..,"aspect":true,"bleed_x":true,"shape":"diagonal"}]
                           bleed      = 全出血（封面），撑满剩余空间
                           不给 height/aspect = 自适应（推荐）：图吃掉本卡剩余空间，整组卡的图底
                              自动对齐；容器同时受「图片按版心宽度缩放后的自然高度」上限约束，
                              横长图不会被为凑高度而左右裁切、切掉画面里的字
                           height     = 固定取景窗口（写了就不再自适应），配 pos 定中心
                                        **在 layout=inline/side 下语义变为「限高上限」**：
                                        图矮于上限就通栏，高于上限就缩到上限并居中，
                                        两种情况都不裁内容。
                                        ⚠ **inline 模式默认别写 height**：写了上限，横图就会被
                                        缩窄到「上限×比例」，于是**图比文字栏窄一截**（实测
                                        952 栏 + height 470 的 16:9 图 → 图宽只有 838），
                                        整组卡图文不齐。不写才通栏 = 与正文同宽。
                                        只有确实想要一张窄图时才用
                           aspect     = 按图片原比例铺满宽度
                           bleed_x    = 仅左右出血（慎用，会与正文左右边距不齐）
                           shape      = 主图轮廓。**默认不写 = 矩形**。仅封面卡用：
                                          none      矩形（默认，等同不写）
                                          diagonal  斜切——上缘左高右低，对角切割
                                          moongate  月洞门——椭圆拱顶
                                          tear      撕纸边——不规则手撕上缘
                                        ⚠ 异形会咬掉**图片自身**的边角字：封面图若是「带排版的
                                        海报」，斜切/拱顶会切掉图内标题。纯摄影/纹理/人像才安全。
                                        图内带字时改用 diagonal 并把切角调小（见 SHAPES）。
        footer_left  str  覆盖页脚左栏
        footer_right str  覆盖页脚右栏

    ※ 元信息行（meta）**两栏都为空则整行不渲染**——默认关闭。
      刊物编号 / 年份这类装饰性信息属于噪音，除非要标明系列（如 "// 提示词解析 · 视觉逻辑 · 创作思路"），否则不要写。

输出：
    <output_dir>/card_NN.png
    <output_dir>/_html/card_NN.html
"""
import json
import os
import random
import subprocess
import sys
from html import escape
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SNAP_BIN = SCRIPT_DIR / "snap"
DEFAULT_FONT = SCRIPT_DIR.parent / "assets" / "SmileySans.otf.ttf"

DEFAULT_NAV = [
    "VISUAL",
    "PROMPT",
    "IMAGE",
    "LAYOUT",
]

# 章节图标**固定**为拼图 emoji，不随文章或情绪变化——
# 卡片组内图标一变，视觉体系立刻散。只有整组换主题时才改这个常量。
DEFAULT_ICON = "🧩"

# ── 字号档（全组只有这几档，不许按卡微调）────────────────────────────
# 2026-09-21 正文换得意黑后整体上调一档：得意黑是窄体，1 全角字实占约 0.79em
# （苹方是 1.0em），同样 26px 排出来比苹方短一截、看着就"小气"。
# 30px 是量出来的：版心 952px ÷ (0.79 × 30) ≈ 40 字/行，正文字感与 56px 标题匹配。
DEFAULT_PARA_SIZE = 30      # 中文叙述（导语/正文/清单内容）——默认，manifest 不写
PROMPT_PARA_SIZE = 22       # 英文提示词/参数——每段显式写 size/lead/color
PROMPT_PARA_LEAD = 1.55

# ── 固定顶隙（报头底线 → 标题墨迹顶）──────────────────────────────────
# 2026-09-23 非叔：「至少保证我们每页的标题和页眉之间距离是一样的，
# 读者的习惯无法更改，都是从上至下看的」。
# 这是 valign:"fixed" 时的默认 padding-top，全组共用同一个数，不许按卡调。
TOP_GAP = 84


# ── 封面异形（默认关，manifest 里 images[].shape 才启用）──────────────
# 只换主图轮廓，出血逻辑不变（左右仍靠 figure 的负 margin）。
# 斜切的方向是踩过坑的：左低右高会切掉图内标题首字，所以固定为左高右低。
#
# 想调斜切角度 / 撕纸深浅，改下面这两个常量即可，全组卡一起生效。
DIAGONAL_CUT = 13.0     # 斜切：上缘右端下移的百分比
TEAR_SEED, TEAR_POINTS, TEAR_DEPTH = 17, 86, 8.0


def tear_edge(seed=TEAR_SEED, n=TEAR_POINTS, depth=TEAR_DEPTH):
    """手撕纸的上缘折线，返回 clip-path 的 polygon() 字符串。

    真实撕边不是等距尖齿，而是「长距离浅裂 + 偶发深撕口」：
    深度按 浅 70% / 中 22% / 深 8% 抽，相邻点再叠一点小扰动，
    右侧整体略收，避免看起来像锯齿剪刀。seed 固定 → 结果可复现。
    """
    rnd = random.Random(seed)
    pts = []
    for i in range(n + 1):
        x = 100.0 * i / n
        t = i / n
        r = rnd.random()
        if r < 0.08:
            y = depth * rnd.uniform(0.95, 1.25)      # 偶发深撕口
        elif r < 0.30:
            y = depth * rnd.uniform(0.50, 0.80)      # 中等裂口
        else:
            y = depth * rnd.uniform(0.10, 0.34)      # 长距离浅裂
        y += rnd.uniform(-0.5, 0.5)                  # 细扰动，破掉规律感
        pts.append((x, max(0.0, y * (1.0 - 0.28 * t))))
    pts.append((100.0, 100.0))
    pts.append((0.0, 100.0))
    return "polygon(" + ",".join("%.2f%% %.2f%%" % p for p in pts) + ")"


SHAPES = {
    "none":     lambda: "",                                       # 矩形 = 默认
    "diagonal": lambda: "clip-path:polygon(0 0,100%% %.2f%%,100%% 100%%,0 100%%)"
                        % DIAGONAL_CUT,
    "moongate": lambda: "border-radius:50% 50% 0 0 / 30% 30% 0 0",
    "tear":     lambda: "clip-path:" + tear_edge(),
}

FONT_SANS = ("-apple-system,'PingFang SC','Hiragino Sans GB','Heiti SC',"
             "'Source Han Sans SC','Noto Sans SC','Microsoft YaHei',sans-serif")


def ensure_snap():
    if SNAP_BIN.exists():
        return str(SNAP_BIN)
    src = SCRIPT_DIR / "snap.swift"
    if not src.exists():
        return None
    subprocess.run(["swiftc", "-O", "-swift-version", "5", str(src), "-o", str(SNAP_BIN)],
                   capture_output=True, text=True, timeout=300)
    return str(SNAP_BIN) if SNAP_BIN.exists() else None


def img_dims(path):
    try:
        out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                             capture_output=True, text=True, timeout=20).stdout
        w = h = 0
        for ln in out.splitlines():
            ln = ln.strip()
            if ln.startswith("pixelWidth:"):
                w = int(ln.split(":")[1])
            elif ln.startswith("pixelHeight:"):
                h = int(ln.split(":")[1])
        if w and h:
            return w, h
    except Exception:
        pass
    return 1000, 1000


def uri(path):
    return "file://" + str(Path(path).resolve()).replace(" ", "%20")


def title_html(lines, size):
    out = []
    for ln in lines:
        if isinstance(ln, dict):
            txt = escape(ln.get("text", ""))
            hl = escape(ln.get("hl", "")) if ln.get("hl") else ""
            if hl and hl in txt:
                a, b = txt.split(hl, 1)
                out.append('%s<span class="hl">%s</span>%s' % (a, hl, b))
            else:
                out.append(txt)
        else:
            out.append(escape(ln))
    return ('<div class="title" style="font-size:%dpx">%s</div>'
            % (size, "".join('<div class="tl">%s</div>' % t for t in out)))


# ── 正文卡的图文构图 ──────────────────────────────────────────────────
# stack  纵向堆叠（默认，老行为）
# inline 嵌入式——图插在段落之间，通栏；过高则限高居中
# side   左右构图——图在一侧、正文在另一侧
#
# **核心约束：inline / side 绝不裁图。**
# 做法是让容器的宽高比与图片完全一致（尺寸由下面按 canvas/pad 折算出绝对
# 像素并写进 inline style），于是 object-fit:cover 退化成"刚好铺满"，一个
# 像素都不切。刻意不用 CSS 百分比链——WebKit 上 height:100% + aspect-ratio
# 在 flex 里会塌，折算成绝对像素才是可复现的。
AVG_CHROME_H = 46 + 46 + 178   # 报头 + 报尾 + 章节块（hd/sub），估算用


def pick_layout(imgs, explicit):
    """决定正文卡的图文构图。

    **不写 = stack**（老行为，绝不改老卡）；要新版式必须显式写 side / inline / auto。
    这条是硬规矩：好醋判定那批已交付的卡不带 layout，它们必须逐像素不变。
    auto 时按首图比例判定，阈值卡在 0.95：竖图（如 3:4 = 0.75）走左右构图，
    横图走嵌入式通栏。
    """
    if not explicit:
        return "stack"
    lay = str(explicit).strip().lower()
    if lay in ("stack", "side", "inline"):
        return lay
    if lay != "auto":
        print("WARN: 未知 layout %r（可选 stack/side/inline/auto），按 stack 处理" % explicit)
        return "stack"
    if not imgs:
        return "stack"
    w0, h0 = img_dims(imgs[0]["path"])
    ratio = (float(w0) / h0) if (w0 and h0) else 1.0
    return "side" if ratio < 0.95 else "inline"


# ── 字体度量（用 colprofile 在真渲出的卡上量的，不是估的）────────────
# 得意黑：1 个全角字实占 0.79em，拉丁含空格平均 0.42em（苹方分别是 1.0 / 0.50）。
# 版心 952px，于是「一行放得下多少字」= 952 ÷ (0.79 × 字号)：
#     30px 中文 → 约 40 字      22px 英文 → 约 103 字符
# 导语长度就照这个卡：30px 下写 32–38 字最稳（满了好看，又不会折行）。
CJK_EM = 0.79
LATIN_EM = 0.42


def est_lines(txt, size, body_w):
    """按字体度量粗估一段文字排几行。只用于自检提示，不当排版尺寸用。"""
    w = sum(CJK_EM if ord(ch) > 0x2E80 else LATIN_EM for ch in str(txt)) * size
    return max(1, int(w / body_w) + (0 if w % body_w == 0 else 1))


def para_html(p, base_size, base_lead):
    """一段正文。字符串＝常规段；dict 可单独覆盖该段字号／行高／墨色／最小行数。

    没有覆盖时不写 style 属性——老卡的 DOM 与 CSS 一字不差，保证像素级回归。
    min_lines：给这一段撑起 N 行的高度。**只在「整组导语确实都是 N 行」时用**。
    拿它给一行就写完的导语补空行，补出来的空档正好落在配图上方，读者看到的就是
    「图文之间的间距过大」（2026-09-21 非叔在《华夏衣冠》卡 7 上就是这么发现的）。
    正确做法是把导语压进一行（30px 下约 38 字以内，见 CJK_EM），而不是补空行。
    """
    ml = 0
    if isinstance(p, dict):
        txt = p.get("text", "")
        size = int(p.get("size", base_size))
        lead = "%g" % float(p.get("lead", base_lead))
        color = p.get("color") or ""
        ml = int(p.get("min_lines", 0) or 0)
    else:
        txt, size, lead, color = p, base_size, base_lead, ""
    rules = []
    if size != base_size or lead != "%g" % float(base_lead) or color:
        rules.append("font-size:%dpx" % size)
        rules.append("line-height:%s" % lead)
        if color:
            rules.append("color:%s" % color)
    if ml:
        rules.append("min-height:%dpx" % round(ml * size * float(lead)))
    st = ' style="%s"' % ";".join(rules) if rules else ""
    return '<p class="para"%s>%s</p>' % (st, escape(txt))


def est_content_bottom(card, cfg, para_size, para_lead):
    """粗估这一卡正文排完后落在哪个 y —— 只给「无图卡内容够不够」的自检用。

    字宽按 CJK_EM / LATIN_EM（得意黑实测值）折算，实测与 `rowprofile` 读数只差
    十几像素，够判断「底部会不会空掉一大片」；不要拿它当排版尺寸。
    """
    W, H = cfg["canvas"]
    padL, padT, padR, padB = cfg["pad"]
    bodyW = W - padL - padR
    y = float(padT) + 46.0 + 178.0        # 报头 + 章节块（hd / sub）
    first = True
    for p in card.get("paras", []):
        if isinstance(p, dict):
            size = int(p.get("size", para_size))
            lead = float(p.get("lead", para_lead))
            txt = str(p.get("text", ""))
            ml = int(p.get("min_lines", 0) or 0)
        else:
            size, lead, txt, ml = para_size, float(para_lead), str(p), 0
        lines = max(ml, est_lines(txt, size, bodyW))
        y += (72.0 if first else 36.0) + lines * size * lead
        first = False
    return y


def list_html(card):
    """无图卡的「条目清单」——细线分隔的参数／要点行。

    它是无图卡撑满版面的主力：行高可以被撑开吸收剩余空间，于是整页从章节名一路
    排到报尾，不会在中间留出「像没写完」的大片空白。
    条目内容必须是文章自己的信息，不许为了填空编凑。
    """
    items = card.get("list") or []
    if not items:
        return ""
    rows = []
    for it in items:
        if isinstance(it, dict):
            k = escape(str(it.get("k", "")))
            v = escape(str(it.get("v", "")))
        else:
            k, v = "", escape(str(it))
        kk = '<span class="k">%s</span>' % k if k else ""
        rows.append('<div class="row">%s<span class="v">%s</span></div>' % (kk, v))
    return '<div class="list">%s</div>' % "".join(rows)


def quote_html(card):
    """无图卡的「金句块」——把原文里最有态度的一句放到配图本该在的位置。

    和旧的 giant 幽灵字不是一回事：这里放的是**文章自己的话**，读者读得懂，
    大字因此是内容而不是占位符。文字必须摘自原文，不许自造口号。
    """
    q = card.get("quote")
    if not q:
        return ""
    if isinstance(q, str):
        q = {"text": q}
    size = int(q.get("size") or 68)
    color = q.get("color") or "#0D0D0D"
    lines = "".join('<div class="ql">%s</div>' % escape(l)
                    for l in str(q.get("text", "")).split("\n"))
    by = ('<div class="by">%s</div>' % escape(str(q["by"]))) if q.get("by") else ""
    return ('<div class="quote" style="font-size:%dpx;color:%s">%s%s</div>'
            % (size, color, lines, by))


def giant_html(card, cfg):
    """无图卡的「大字替身」：用超大汉字／拉丁字占据本该放配图的那块版面。

    原文某个章节没配图时，千万别靠放大正文字号去填——那会让整组字号失控
    （被否过）。改用大字块：块高与同组配图的自然高一致，于是各卡版面节奏仍对齐。
    """
    g = card.get("giant")
    if not g:
        return ""
    if isinstance(g, str):
        g = {"text": g}
    W, H = cfg["canvas"]
    padL, padT, padR, padB = cfg["pad"]
    bodyW = W - padL - padR
    txt = g.get("text", "")
    gh = int(g.get("height") or 534)
    # 默认字号：块高优先（大字是骨架），横向超出交给块边裁掉——
    # 「被画面边缘裁切、只露局部笔画」正是这套美学的做法。给了 size 就照用。
    size = int(g.get("size") or min(gh * 0.92, bodyW / max(1, len(txt))))
    color = g.get("color") or "#EDEDED"
    align = g.get("align") or "center"
    return ('<div class="giant" style="height:%dpx;font-size:%dpx;color:%s;'
            'justify-content:%s">%s</div>'
            % (gh, size, color, align, escape(txt)))


def figure_html(im, cfg, layout="stack"):
    """一张配图。layout 决定容器尺寸怎么定；inline/side 下宽高比严格等于图片比例。"""
    W, H = cfg["canvas"]
    padL, padT, padR, padB = cfg["pad"]
    bodyW = W - padL - padR

    ble = bool(im.get("bleed"))
    fixed = bool(im.get("height") or im.get("aspect"))
    cls = "figure"
    if ble:
        cls += " bleed"
    elif im.get("bleed_x"):
        cls += " wide"
    if fixed and not ble and layout not in ("inline", "side"):
        cls += " fixed"
    styles = []

    if layout in ("inline", "side") and not ble:
        # 不裁模式：容器的宽高比做成和图片一模一样，图就"刚好铺满"，零裁切。
        # 这里的 height 是**限高上限**（不是裁切窗口）——图矮于上限就通栏，高于上限就
        # 按上限缩、居中。两种情况都不切内容。
        w0, h0 = img_dims(im["path"])
        ratio = float(w0) / h0 if h0 else 1.0
        avail = max(200.0, H - padT - padB - AVG_CHROME_H)
        if layout == "side":
            # 侧栏：宽度先卡到版心的一个比例，再回看高度有没有超上限。
            # 默认 0.62/0.92 是量出来的——图占满可用高度的大半，只留约 100px 呼吸，
            # 同时文字栏还剩 ~318px（30px 中文约 9 字/行），仍读得下去。
            wmax = bodyW * float(im.get("side_w", cfg.get("side_w", 0.62)))
            hcap = float(im.get("height")
                         or avail * float(im.get("side_fill", cfg.get("side_fill", 0.92))))
            hpx = min(wmax / ratio, hcap)
            wpx = hpx * ratio
        else:
            # 嵌入式：先试通栏；按比例算出的高度超过上限就改成限高居中
            nh = bodyW / ratio
            hcap = float(im.get("height") or avail * 0.60)
            if nh <= hcap:
                wpx, hpx = float(bodyW), nh
            else:
                hpx = hcap
                wpx = hpx * ratio
                cls += " narrow"
        styles.append("width:%dpx;height:%dpx" % (round(wpx), round(hpx)))
    elif fixed and not ble:
        if im.get("aspect"):
            w0, h0 = img_dims(im["path"])
            styles.append("aspect-ratio:%d/%d" % (w0, h0))
        else:
            styles.append("height:%dpx" % im["height"])
    elif not ble:
        # 老 stack 行为：填满剩余空间，但不超过图片按版心宽缩放后的自然高度——
        # 否则横长图会为凑高度而被左右裁切，切掉画面里的字。
        w0, h0 = img_dims(im["path"])
        if w0 and h0:
            nat = int(round(bodyW * float(h0) / w0))
            styles.append("max-height:%dpx" % nat)

    # 封面异形：inline style 优先级高于 .figure .ph 的默认 border-radius
    shape = (im.get("shape") or "").strip().lower() or "none"
    if shape not in SHAPES:
        print("WARN: 未知 shape %r（可选 %s），按矩形处理"
              % (im.get("shape"), "/".join(SHAPES)))
        shape = "none"
    sh = SHAPES[shape]()
    if sh:
        styles.append(sh)
    ph_style = ' style="%s"' % ";".join(styles) if styles else ""
    img_style = ' style="object-position:%s"' % im["pos"] if im.get("pos") else ""
    cap = ('<figcaption>%s</figcaption>' % escape(im["caption"])
           if im.get("caption") else "")
    return ('<figure class="%s"><div class="ph"%s><img src="%s"%s></div>%s</figure>'
            % (cls, ph_style, uri(im["path"]), img_style, cap))


def build_html(card, cfg):
    W, H = cfg["canvas"]
    brand = cfg["brand"]
    padL, padT, padR, padB = cfg["pad"]
    # 本卡正文规格覆盖（默认 = 常规论点卡的 30px / 1.7，见 SKILL.md 字号档）；
    # 提示词卡这类长文附录会给 para_size/para_lead，让一张卡收得下整条提示词。
    para_size = int(card.get("para_size", DEFAULT_PARA_SIZE))
    para_lead = "%g" % float(card.get("para_lead", 1.7))

    nav_html = "".join('<span>%s</span>' % escape(n).replace("\n", "<br>")
                       for n in cfg["nav"])

    meta_left = card.get("meta_left", "")
    meta_right = card.get("meta_right", cfg.get("meta_right", ""))

    head = ['<header class="masthead">']
    logo = ('<img class="mark" src="%s" style="height:%dpx">'
            % (uri(brand["logo"]), brand.get("logo_h", 52))) if brand.get("logo") else ""
    head.append('<div class="top">%s<div class="nav">%s</div></div>'
                % (logo, nav_html))
    if meta_left or meta_right:
        head.append('<div class="meta"><span>%s</span><span>%s</span></div>'
                    % (escape(meta_left), escape(meta_right)))
    if card.get("rule"):
        head.append('<div class="rule"></div>')
    head.append('</header>')

    paras = card.get("paras", [])
    imgs = card.get("images", [])
    lay = pick_layout(imgs, card.get("layout"))
    # 无图卡：版面靠 list 条目 / quote 金句撑满；正文容器因此拿到 .nofig，
    # 让清单能把剩余高度吃掉，整页不会在中间留出「像没写完」的空洞。
    nofig = (not imgs) and bool(card.get("list") or card.get("quote"))
    if not imgs and not nofig:
        # 底部还空着 400px 以上 → 正文太少，这页会「像没写完」。补 list / quote，别硬渲。
        slack = (H - padB - 34.0) - est_content_bottom(card, cfg, para_size, para_lead)
        if slack > 400:
            print("WARN: 无配图的卡正文排完后底部还空着约 %dpx —— 请补 list 条目或 "
                  "quote 金句（见 SKILL.md「无配图的卡」）" % round(slack))

    # 自检：全组字号只有两档（中文 30 / 英文提示词 22）。冒出别的数就是又按卡调了字号
    # ——那正是「整组看着像草稿」的来源（2026-09-21 被非叔否掉）。
    for p in paras:
        if not isinstance(p, dict) or "size" not in p:
            continue
        s = int(p["size"])
        if s not in (para_size, DEFAULT_PARA_SIZE, PROMPT_PARA_SIZE):
            print("WARN: 一段的字号是 %dpx —— 全组只允许 %dpx（中文叙述）/%dpx（英文提示词）"
                  "两档，长文请改拆卡，不要按卡调字号" % (s, DEFAULT_PARA_SIZE, PROMPT_PARA_SIZE))

    # 自检：min_lines 比自然行数多 → 段末留一条空档，而这条空档正好落在配图上方，
    # 读者看到的就是「图文之间间距过大」（2026-09-21 非叔在《华夏衣冠》卡 7 发现）。
    for p in paras:
        if not isinstance(p, dict):
            continue
        ml = int(p.get("min_lines", 0) or 0)
        if not ml:
            continue
        txt = str(p.get("text", ""))
        size = int(p.get("size", para_size))
        bodyW = W - padL - padR
        nat = est_lines(txt, size, bodyW)
        if ml > nat:
            print("WARN: 一段的 min_lines=%d，但它只排得下 %d 行 —— 段末多出约 %dpx "
                  "空档，就在配图上方，看着就是间距过大。把这段缩到 %d 行即可"
                  "%s；或者让全组导语都写满 %d 行"
                  % (ml, nat, round((ml - nat) * size * float(para_lead)), nat,
                     ("（%dpx 下写 %d 字以内）" % (size, int(bodyW / (CJK_EM * size) * 0.92))
                      if nat == 1 else ""), ml))

    # 全出血的封面卡不参与垂直居中：bleed 图的语义就是撑满到底，
    # 一居中它就不吃剩余空间、图下方空出一大条（2026-09-23 实测底隙 155px）。
    bleed_first = bool(imgs and imgs[0].get("bleed"))
    _v = str(card.get("valign", cfg.get("valign", "top"))).lower()
    if _v in ("fixed", "flow", "topgap"):
        # 固定顶隙：全组每页「报头 → 标题」距离完全一致，内容顺排向下
        gap = int(card.get("top_gap", cfg.get("top_gap", TOP_GAP)))
        cls = " fix\" style=\"padding-top:%dpx" % gap
    else:
        cls = " ctr" if (_v == "center" and not bleed_first) else ""
    body = ['<div class="body%s%s">' % (" nofig" if nofig else "", cls)]

    if card.get("title"):
        body.append(title_html(card["title"], card.get("title_size", 70)))
    if card.get("latin"):
        body.append('<div class="latin" style="font-size:%dpx">%s</div>'
                    % (card.get("latin_size", 116), escape(card["latin"])))

    if card.get("heading") or card.get("subtitle"):
        icon = '<span class="ic">%s</span>' % (card.get("icon") or DEFAULT_ICON)
        hd = ('<div class="hd">%s%s</div>' % (icon, escape(card.get("heading", "")))
              if card.get("heading") else "")
        sub = ('<div class="sub">%s</div>' % escape(card["subtitle"])
               if card.get("subtitle") else "")
        body.append(hd + sub)

    def fig(im, mode="stack"):
        return figure_html(im, cfg, mode)

    if lay == "side" and imgs and not imgs[0].get("bleed"):
        # 左右构图：图与正文并排。图垂直居中，正文填满另一侧那一栏。
        col = ('<div class="col">%s</div>'
               % "".join(para_html(p, para_size, para_lead) for p in paras))
        first = fig(imgs[0], "side")
        inner = ((first + col) if (card.get("side") or "left").lower() == "left"
                 else (col + first))
        body.append('<div class="split">%s</div>' % inner)
        for im in imgs[1:]:
            body.append(fig(im))
    else:
        # inline：图插在第 image_at 段之后（默认首段之后）；stack：图统一在全部段落之后
        at = len(paras)
        if lay == "inline" and not (imgs and imgs[0].get("bleed")):
            at = max(0, min(int(card.get("image_at", 1)), len(paras)))
        body.append("".join(para_html(p, para_size, para_lead) for p in paras[:at]))
        for im in imgs:
            mode = "inline" if (lay == "inline" and not im.get("bleed")) else "stack"
            body.append(fig(im, mode))
        if not imgs:
            # 无图卡：配图那块版面交给「文章自己的内容」——先条目清单，再金句。
            # giant 只在作者显式要求时才渲染（旧做法，大字会被页边裁掉、看着像没写完）
            body.append(list_html(card))
            body.append(quote_html(card))
            body.append(giant_html(card, cfg))
        body.append("".join(para_html(p, para_size, para_lead) for p in paras[at:]))

    body.append('</div>')

    # 报尾中栏：含 "｜" 就拆成「浅灰常规 + 高亮品牌名」两段，否则整串走高亮
    cr = brand["copyright"]
    if "｜" in cr:
        cr_l, cr_r = cr.split("｜", 1)
        cr_html = ('<span class="cy">%s ｜ </span><i>%s</i>'
                   % (escape(cr_l.strip()), escape(cr_r.strip())))
    else:
        cr_html = '<i>%s</i>' % escape(cr)

    foot = ('<footer>'
            '<span class="fl">%s</span>'
            '<span class="fc">%s</span>'
            '<span class="fr">%s</span>'
            '</footer>' % (escape(card.get("footer_left", cfg["footer_left"])),
                           cr_html,
                           escape(card.get("footer_right", cfg["footer_right"]))))

    css = """
*{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased}
@font-face{font-family:'Disp';src:url('%(font)s') format('truetype');font-weight:400}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#fff}
.card{position:relative;width:%(W)dpx;height:%(H)dpx;background:#fff;
  padding:%(pT)dpx %(pR)dpx %(pB)dpx %(pL)dpx;
  display:flex;flex-direction:column;
  font-family:%(sans)s;color:#111}
.masthead{flex:0 0 auto}
.top{display:flex;align-items:center;gap:80px}
.mark{display:block;height:46px;width:auto;flex:0 0 auto}
.nav{flex:0 0 auto;margin-left:auto;display:flex;align-items:baseline;gap:52px;
  font-size:12.5px;font-weight:500;letter-spacing:.22em;line-height:1.35;color:#1A1A1A}
.meta{display:flex;justify-content:space-between;align-items:baseline;
  margin-top:32px;font-size:14px;letter-spacing:.08em;color:#ABABAB;
  text-transform:uppercase}
.rule{margin-top:22px;height:1px;background:#EAEAEA}
.body{flex:1 1 auto;display:flex;flex-direction:column;min-height:0}
/* 版心垂直居中（valign:center）：报头与报尾对称，中间才是文字和图。
   不开时维持老行为——内容从顶部一路排到底，余量全被图吃掉，于是底部贴报尾
   而顶部松，看着头重脚轻（2026-09-23 压花玻璃卡组非叔指出）。 */
.body.ctr{justify-content:center;padding-top:8px}
.body.ctr .figure,.body.ctr .figure .ph,.body.ctr .split{flex:0 0 auto}
/* 清单/金句在居中模式下也不许吃掉剩余空间——吃掉了就会在底部堆出一大块白
   （实测卡 8 底隙 320px、卡 10 269px）。居中的活交给 .body 整体做。
   特异性必须写足（.body.ctr.nofig），否则被后面的 .body.nofig 规则盖回去。 */
.body.ctr .list,.body.ctr .quote,
.body.ctr.nofig .list,.body.ctr.nofig .quote{flex:0 0 auto}
.body.ctr .list .row,
.body.ctr.nofig .list .row{flex:0 0 auto;max-height:none}
/* 固定顶隙（valign:"fixed"，**2026-09-23 非叔定的新默认**：「保证每页的标题和
   页眉之间距离是一样的」——读者从上往下看，阅读起点必须每页一致）。
   做法是给 .body 一个固定的 padding-top，内容从标题顺排向下，余量全留在底部。
   与 ctr 的区别：ctr 每页顶隙随内容高度浮动（内容多的页顶隙小、内容少的页顶隙大），
   翻组时标题会上下跳；fixed 顶隙恒定，底隙才随内容走。 */
.body.fix{justify-content:flex-start}
.body.fix .figure,.body.fix .figure .ph,.body.fix .split{flex:0 0 auto}
.body.fix .list,.body.fix .quote,
.body.fix.nofig .list,.body.fix.nofig .quote{flex:0 0 auto}
.body.fix .list .row,
.body.fix.nofig .list .row{flex:0 0 auto;max-height:none}
/* 顶隙由 padding-top 独占，.hd 自带的那 60px 必须归零，否则顶隙 = 设定值 + 60 */
.body.fix > .hd,.body.fix > .title{margin-top:0}
.title{margin-top:30px;font-family:'Disp';font-weight:400;line-height:1.2;
  letter-spacing:.015em;color:#0D0D0D;margin-bottom:4px}
.tl{white-space:nowrap}
.hl{background:#0D0D0D;color:#fff;padding:0 .09em}
.latin{margin-top:8px;font-family:'Disp';font-weight:400;line-height:1;
  letter-spacing:.005em;color:#0D0D0D;white-space:nowrap}
.hd{margin-top:60px;font-family:'Disp';font-weight:400;font-size:56px;
  line-height:1.15;letter-spacing:.015em;color:#0D0D0D;
  display:flex;align-items:center;gap:14px}
.ic{font-family:%(sans)s;font-size:48px;line-height:1}
.sub{margin-top:20px;font-family:'Disp';font-size:34px;font-weight:400;
  color:#A3A3A3;letter-spacing:.02em}
/* 三级空隙（必须拉开量级，否则整页只是一串等距的句子，标题失去统辖力）：
     标题 ↔ 正文  72px   ← 章节开场，最大
     段   ↔ 段    36px   ← 换意，中等（视觉约 54px）
     行   ↔ 行    行高 1.7 折出约 18px
   比例约 4 : 3 : 1。正文首段绝不能沿用 36px 的段距——那样标题和段落同级。 */
.para{margin-top:36px;font-family:'Disp';font-weight:400;font-size:%(ps)dpx;
  line-height:%(pl)s;color:#1D1D1D;letter-spacing:.005em;text-align:left}
.hd + .para,.sub + .para{margin-top:72px}
.figure{margin-top:36px;display:flex;flex-direction:column;
  flex:1 1 auto;min-height:0}
.para + .figure{margin-top:48px}
.figure .ph{border-radius:14px;overflow:hidden;background:#F5F5F5;
  flex:1 1 auto;min-height:0}
.figure img{width:100%%;height:100%%;object-fit:cover;display:block;
  object-position:center}
.figure.fixed{flex:0 1 auto}
.figure.fixed .ph{flex:0 0 auto}
.figure.bleed{flex:1 1 auto;min-height:0;
  margin-left:-%(pL)dpx;margin-right:-%(pR)dpx}
.figure.bleed .ph{flex:1 1 auto;min-height:0;border-radius:0}
.figure.wide{margin-left:-%(pL)dpx;margin-right:-%(pR)dpx}
.figure.wide .ph{border-radius:0}
/* 正文卡图文构图（layout: inline / side）
   尺寸由 render.py 按 canvas/pad 折算成绝对像素，容器宽高比**严格等于图片比例**，
   于是 object-fit:cover 退化成"刚好铺满"，一个像素都不切。
   刻意不写 aspect-ratio + height:100%% 这类百分比链——WebKit 在 flex 里会塌。 */
.figure.inline{flex:0 0 auto;justify-content:center}
.figure.inline .ph{flex:0 0 auto}
.figure.inline.narrow{align-self:center}
/* 无图卡的「大字替身」：占住本该放配图的那一块，块高与配图自然高一致，
   于是同一组卡里「有图的」和「没图的」版面节奏仍然对齐。 */
.giant{flex:0 0 auto;display:flex;align-items:center;overflow:hidden;
  margin-top:48px;font-family:'Disp';font-weight:400;line-height:1;
  letter-spacing:.02em;white-space:nowrap}
/* 无图卡的「条目清单」：细线分隔的要点／参数行。
   它是无图卡撑满版面的主力——行高可被撑开吸收剩余空间，于是整页从章节名一路排到
   报尾，中间不留「像没写完」的灰白空洞（2026-09-21 非叔否掉旧的幽灵大字占位）。 */
.list{margin-top:72px;display:flex;flex-direction:column;
  border-top:1px solid #E6E6E6}
/* 清单紧跟在正文段之后时，顶端要与同组配图的顶边**齐平**（都是 48px）——
   整组卡翻下来，「有图的」和「没图的」内容起始线在同一条水平线上。 */
.para + .list{margin-top:48px}
.list .row{display:flex;align-items:center;gap:36px;padding:24px 0;
  border-bottom:1px solid #E6E6E6}
.list .k{flex:0 0 auto;min-width:132px;font-family:'Disp';font-size:17px;
  font-weight:400;letter-spacing:.14em;color:#A3A3A3}
.list .v{flex:1 1 auto;font-family:'Disp';font-size:30px;line-height:1.6;
  color:#1D1D1D;letter-spacing:.005em}
/* 清单只在无图卡里撑开；有图的卡里它保持自然行高 */
.body.nofig .list{flex:1 1 auto;min-height:0}
.body.nofig .list .row{flex:1 1 auto;max-height:200px}
/* 无图卡的「金句块」：把原文里最有态度的一句放到配图本该在的位置。
   放的是文章自己的话，所以大字是内容、不是占位符。 */
.quote{margin-top:48px;font-family:'Disp';font-weight:400;line-height:1.22;
  letter-spacing:.015em}
.para + .quote{margin-top:48px}
.quote .ql{white-space:nowrap}
.quote .by{margin-top:18px;font-family:'Disp';font-size:17px;font-weight:400;
  color:#A3A3A3;letter-spacing:.14em}
/* 无图卡里 quote 也要像 list 一样吃掉剩余空间（垂直居中），
   否则金句贴在正文后、下方留一大片灰白空洞（2026-09-22 压花玻璃卡组实测）。 */
.body.nofig .quote{flex:1 1 auto;min-height:0;display:flex;
  flex-direction:column;justify-content:center}
.split{display:flex;gap:44px;flex:1 1 auto;min-height:0;margin-top:48px;
  align-items:center}
.split .figure{margin-top:0;flex:0 0 auto;justify-content:center}
.split .col{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;
  justify-content:center}
.split .col .para{margin-top:36px}
.split .col .para:first-child{margin-top:0}
figure figcaption{margin-top:14px;text-align:center;font-family:'Disp';
  font-size:15px;letter-spacing:.14em;color:#9A9A9A;flex:0 0 auto}
footer{flex:0 0 auto;display:flex;align-items:center;padding-top:16px;
  font-size:15px;letter-spacing:.14em;color:#1A1A1A;text-transform:uppercase}
footer .fl{flex:1 1 0}
footer .fr{flex:1 1 0;text-align:right}
footer .fc{flex:0 0 auto;text-transform:none;letter-spacing:.04em}
/* 报尾整条同一墨色 #1A1A1A——参考图页脚就是近黑，不是灰。
   版权段与品牌名只靠字重分层级，不再靠颜色差。 */
footer .fc .cy{font-size:15px;font-weight:400;color:#1A1A1A;letter-spacing:.06em}
footer .fc i{font-style:normal;font-size:15px;font-weight:600;color:#1A1A1A;
  white-space:nowrap}
""" % {"W": W, "H": H, "pL": padL, "pT": padT, "pR": padR, "pB": padB,
       "sans": FONT_SANS, "font": uri(cfg["display_font"]),
       "ps": para_size, "pl": para_lead}

    return ("<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
            "<style>%s</style></head><body><div class=\"card\">%s%s%s</div></body></html>"
            % (css, "".join(head), "".join(body), foot))


def main():
    if len(sys.argv) < 2:
        print("usage: render.py <manifest.json>")
        sys.exit(2)
    mf = Path(sys.argv[1])
    cfg = json.loads(mf.read_text(encoding="utf-8"))
    cfg.setdefault("canvas", [1080, 1440])
    cfg.setdefault("pad", [64, 56, 64, 40])
    cfg.setdefault("nav", DEFAULT_NAV)
    cfg.setdefault("footer_left", "AIGC COLLECTION")
    cfg.setdefault("footer_right", "ART DIRECTION")
    cfg.setdefault("meta_right", "")
    if not cfg.get("display_font") or not Path(cfg["display_font"]).exists():
        cfg["display_font"] = str(DEFAULT_FONT)
    b = cfg.setdefault("brand", {})
    b.setdefault("name", "非叔Design")
    b.setdefault("logo", str(SCRIPT_DIR.parent / "assets" / "logo-feishu.png"))
    b.setdefault("logo_h", 46)
    b.setdefault("copyright", "Copyright © 2026 ｜ 非叔Design")

    out = Path(cfg["output_dir"])
    os.makedirs(out, exist_ok=True)
    os.makedirs(out / "_html", exist_ok=True)

    snap = ensure_snap()
    if not snap:
        print("ERROR: snap 截图器不可用（swiftc 编译失败）")
        sys.exit(3)

    W, H = cfg["canvas"]
    ok = True
    for i, card in enumerate(cfg["cards"], 1):
        html = build_html(card, cfg)
        hp = out / "_html" / ("card_%02d.html" % i)
        hp.write_text(html, encoding="utf-8")
        png = out / ("card_%02d.png" % i)
        r = subprocess.run([snap, str(hp), str(png), str(W), str(H)],
                           capture_output=True, text=True, timeout=120)
        status = r.stdout.strip()
        print("card_%02d -> %s %s" % (i, png.name, status))
        if status != "OK":
            ok = False
            print("   stderr:", r.stderr.strip()[:300])
    print("DONE" if ok else "DONE_WITH_ERRORS")


if __name__ == "__main__":
    main()
