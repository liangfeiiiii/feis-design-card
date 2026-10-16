# feis-design-card

把一篇文章拆成一组「东方编辑刊物」风知识卡片，渲染成 PNG，直接可发小红书。
这是「非叔的AIGC」在用的出卡技能，本文档也是技能本身的说明书。

## 出什么样的卡

- 3:4，1080×1440，版心 952，小红书信息流里不裁切
- 报头四栏英文导航，左上角书法 logo，超大得意黑标题（可局部黑底反白）
- 章节图标固定 🧩，图注浅灰小字，报尾三栏（栏目名 ｜ Copyright ｜ 英文）
- 配图与正文等宽，图顶全组对齐；无图卡用清单或金句撑满
- 版心纵向排布默认 `valign:"fixed"` + `top_gap:56`，每页顶隙完全一致

## 目录结构

```
feis-design-card/
├── SKILL.md                          # 完整规格：版式、manifest 字段、踩坑记录
├── assets/
│   ├── SmileySans.otf.ttf            # 得意黑（SIL OFL 开源许可）
│   └── logo-feishu*.png              # 书法 logo
├── examples/
│   ├── manifest.example.json         # 基础版式示例（stack / list / quote）
│   └── manifest.inline.example.json  # 通栏配图版式示例
└── scripts/
    ├── render.py                     # 渲染主脚本：manifest.json → PNG
    ├── snap.swift + snap             # WebKit 截图（编译好的二进制）
    ├── logo.swift + logo             # 书法 logo 生成
    ├── gap                           # 验版：量顶隙 / 底隙
    ├── rowprofile.swift + rowprofile # 验版：行剖面
    ├── colprofile.swift + colprofile # 验版：列剖面
    └── pixdiff.swift + pixdiff       # 验版：像素比对
```

## 安装

把 `feis-design-card/` 整个目录放进宿主的技能目录：

- WorkBuddy：`~/.workbuddy/skills/feis-design-card/`
- Trae：`~/.trae-cn/skills/feis-design-card/`

macOS 自带 WebKit 和 Swift，无需装任何第三方包。

## 用法

1. 按 `examples/` 里的字段写一份 `manifest.json`（文章拆卡：封面、论点卡、提示词卡等）
2. 渲染：

```bash
python3 scripts/render.py manifest.json
```

3. 验版：

```bash
scripts/gap                 # 顶隙 / 底隙，顶隙全组必须相等
scripts/rowprofile card_02.png 235 6   # 行剖面，验三档空隙
scripts/pixdiff a.png b.png # 两次渲染是否一致
```

## 两个经验

- **渲染不要在沙盒里跑。** WebKit 截图需要非沙盒执行，沙盒里会静默失败或产出空图。
- **别用字节数判断两次渲染是否一致。** 同一台机器不同时间渲出的 PNG 字节数可以差 2%，画面其实只差一层均匀色偏，这是色彩管理不是包坏了。比对请用 `pixdiff`，它看像素。

## 许可

- 脚本与文档：随意用，署名不署名都行，署名更好（非叔的AIGC）
- 得意黑 Smiley Sans：SIL Open Font License，许可文本见[官方仓库](https://github.com/atelier-anchor/smiley-sans)
