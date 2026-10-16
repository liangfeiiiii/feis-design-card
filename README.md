<div align="center">

# feis-design-card.skill

> *"文章是好文章，但读者在小红书里是刷，不是读。拆成一沓卡，每张只说一件事，他才翻得完。"*
> *—— 非叔的AIGC*

[![Skill](https://img.shields.io/badge/Skill-Agent%20Skill-8A2BE2)](#安装)
[![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB)](#环境要求)
[![License](https://img.shields.io/badge/License-署名授权-FF8C00)](#版权)

<br>

**一篇文章进，一沓 3:4 刊物卡出。不是模板拼贴，是一套有报头、版心、页脚的完整刊物版式。**

得意黑大标题、四栏英文报头、圆角配图与正文等宽、报尾三栏收底。
文章按论点拆卡，渲染成 1080×1440 的 PNG，直接可发小红书。

**一次渲染一组**：单张是卡，多张是一组，顶隙全组对齐，每个数字都能用验版工具量出来。

[看效果](#效果示例) · [安装](#安装) · [怎么用](#怎么用) · [卡片是怎么排的](#卡片是怎么排的) · [版权](#版权)

</div>

---

## 效果示例

> 输入一份 manifest，下面是一张卡上排出来的内容。

### 卡片报头

左上角书法 logo，右侧四栏英文导航单词，页眉一条细线压住版心顶部。

### 卡片正文

超大得意黑标题（可局部黑底反白），下面接正文。
正文只有两档字号：中文 30px，英文提示词 22px，全组统一，不按卡微调。

### 卡片配图

圆角、与正文等宽 952px，横图通栏、竖图旁栏，图下浅灰小字图注。
无图的卡用清单或金句撑版面，不放大字号凑数。

一张 manifest 长这样：

```json
{
  "valign": "fixed",
  "top_gap": 56,
  "cards": [
    {
      "no": "03",
      "title": ["压迫感", "从哪来"],
      "paras": [{ "text": "顶天立地，人物高占画面九成。" }],
      "list": ["顶天立地，人物高占画面九成", "低机位仰拍", "大面积留白", "前景遮挡"],
      "quote": "压迫感不靠画质，靠人物在画面里占多大。"
    }
  ]
}
```

> 一次渲染一组卡，报头、正文、配图、报尾四件事各归各位。

---

## 安装

不用敲命令。打开你的 Agent 对话框，把下面这句话连同链接发给它：

```
请帮我安装这个技能：https://github.com/liangfeiiiii/feis-design-card
```

剩下的事 Agent 自己会做。装完它会告诉你一声。

然后丢文章过去就能触发：

```text
> 把这篇文章做成知识卡片
> 这篇 md 拆卡，用非叔的刊物版式
> 出卡，配图用这几张
```

<details>
<summary>老手想自己动手？</summary>

```bash
npx skills add liangfeiiiii/feis-design-card
```

或者手动把 `feis-design-card/` 文件夹放进 Agent 的技能目录（WorkBuddy 是 `~/.workbuddy/skills/`，Trae 是 `~/.trae-cn/skills/`）。

</details>

---

## 怎么用

写一份 `manifest.json`（照 `examples/` 里的样例改），一条命令渲染一组：

```bash
python3 scripts/render.py manifest.json
```

| 字段 | 必填 | 说明 |
|------|------|------|
| no | 是 | 卡片序号，决定输出文件名 card_01.png |
| title | 是 | 标题，数组按行拆，支持局部黑底反白 |
| paras | 否 | 正文段落，中文 30px / 英文 22px 自动分档 |
| list | 否 | 清单条目，无图卡用它撑版面 |
| quote | 否 | 金句，单独一块，配浅色底 |
| figure | 否 | 配图：src、caption、layout（stack / inline / auto / side） |
| rule | 否 | 封面分章线 |
| valign | 组级 | 版心排布，新卡组用 fixed |
| top_gap | 组级 | 页眉到标题的顶隙，默认 56，全组每页一致 |

**渲染后验版**（数字说话，不靠肉眼）：

```bash
scripts/gap                              # 顶隙 / 底隙，顶隙全组必须相等
scripts/rowprofile card_02.png 235 6     # 行剖面，验空隙档位
scripts/pixdiff a.png b.png              # 两次渲染是否一致
```

`gap` 输出每张卡的顶隙、底隙、差值。顶隙全组相等，底隙收在顶隙 ±60px 内，这组卡就算过关。

---

## 卡片是怎么排的

### 一张卡，四层

| 区域 | 内容 | 规格 |
|------|------|------|
| 报头 | 书法 logo + 四栏英文导航 | 细线压顶，全组统一 |
| 版心 | 标题 + 正文 / 配图 | 952px 版心，3:4 画幅居中 |
| 图注 | 配图下方小字 | 浅灰，纯文字无符号 |
| 报尾 | 栏目名 ｜ Copyright ｜ 英文 | 墨色条，压住版心底边 |

### 三个排版细节

1. **字号只有两档**。中文 30px、英文 22px，全组统一。内容多就拆卡，不缩字号，塞爆一张卡不如多出一张。
2. **空隙分三档**。标题到正文、段落到段落、行到行，三档间距比例 4:3:1，靠验版工具量出来，不靠感觉调。
3. **顶隙全组对齐**。fixed 模式下每页页眉到标题的距离完全一致，翻页时标题不跳。封面单独走 top 模式，出血图压到报尾。

### 页脚

报尾墨色条里三栏：左端栏目名，中间 `Copyright © 2026 ｜ 非叔Design`，右端英文。一左一右撑住版面底边。

---

## 环境要求

- macOS（渲染走系统 WebKit，不用装浏览器）
- Python 3.6+
- 验版工具已编译好放 `scripts/`，源码（.swift）在旁边，改了可以自己重编
- 中文用得意黑（SmileySans），已随包附带，SIL OFL 开源许可

**注意：渲染不要在沙盒里跑。** WebKit 截图需要非沙盒执行，沙盒里会静默失败或产出空图。

## 仓库结构

```
feis-design-card/
├── SKILL.md                          # 完整规格：版式、manifest 字段、踩坑记录
├── assets/
│   ├── SmileySans.otf.ttf            # 得意黑（SIL OFL）
│   └── logo-feishu*.png              # 书法 logo
├── examples/
│   ├── manifest.example.json         # 基础版式示例（stack / list / quote）
│   └── manifest.inline.example.json  # 通栏配图版式示例
└── scripts/
    ├── render.py                     # 渲染主脚本，唯一入口
    ├── snap.swift + snap             # WebKit 截图
    ├── logo.swift + logo             # 书法 logo 生成
    ├── gap                           # 验版：顶隙 / 底隙
    ├── rowprofile.swift + rowprofile # 验版：行剖面
    ├── colprofile.swift + colprofile # 验版：列剖面
    └── pixdiff.swift + pixdiff       # 验版：像素比对
```

---

## 版权

**作者：非叔的AIGC　版权所有，转载请保留署名**

技能文件与文档著作权归作者所有，转发和二次分发请保留署名。
用它做出来的卡片，版权归你。

## 关于作者

**非叔的AIGC** — 提示词工程与 AIGC 内容创作

| 平台 | 链接 |
|------|------|
| GitHub | [liangfeiiiii](https://github.com/liangfeiiiii) |
