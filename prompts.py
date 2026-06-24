import json
import os
from config import FB_SPECS, FB_CTA_BUTTONS, COMPLIANCE_RULES, OBJECTIVES, MARKETING_TYPES, FORM_SUBJECTS

_HERE = os.path.dirname(os.path.abspath(__file__))

# 内联参考 Hook（只教结构与写法，模型须 100% 原创，严禁抄袭）。不依赖 Google Drive。
REFERENCE_HOOKS = """[教育] Hook:"别让孩子的数学，拖垮整张 SPM 成绩单 📚" | 结构:恐惧Hook → 痛点共鸣 → 教学方法 → 名师/成效 → 免费试课CTA | CTA:"📲 私讯预约免费试课"
[教育] Hook:"孩子上了中学才发现，基础早就漏了一大半…" | 结构:共鸣Hook → 场景痛点 → 解决方案 → 名额有限紧迫感 → WhatsApp CTA | CTA:"📲 WhatsApp 了解课程"
[教育] Hook:"在家也能跟上学校进度，不用赶来赶去 kan？" | 结构:便利Hook → 线上优势分点 → 社会证明 → 软性私讯CTA | CTA:"💬 私讯领取试课名额\""""


def load_library():
    with open(os.path.join(_HERE, "success_library.json"), encoding="utf-8") as f:
        return json.load(f)


def _label(items, _id):
    for it in items:
        if it["id"] == _id:
            return it["label"]
    return _id


def match_case(library, objective, industry):
    ads = library.get("ads", [])
    for a in ads:
        if a["objective"] == objective and a["industry"] == industry:
            return a
    for a in ads:
        if a["objective"] == objective:
            return a
    for a in ads:
        if a["industry"] == industry:
            return a
    return ads[0] if ads else None


# ---- Gate 1: the write-up prompt fed to ChatGPT-5.4 ------------------------
def build_writeup_prompt(brief, selections, matched=None):
    obj = _label(OBJECTIVES, selections["objective"])
    mtype = _label(MARKETING_TYPES, selections["marketingType"])
    form_focus = selections.get("formDesc") or "Form 1 到 Form 5（全阶段）"
    level_subjects = FORM_SUBJECTS.get(selections.get("formId"), FORM_SUBJECTS["f1_f5"])
    chosen = selections.get("subjects") or []
    if chosen:
        # 只把用户选的科目交给模型；不暴露该年级其他科目，避免文案乱列。
        subjects = "、".join(chosen)
        focus_line = ("- 【重要】本次广告只能围绕以上科目展开，绝不可提及任何其他科目（包括同年级的其它科）。"
                      "标题、正文、卖点都只聚焦这些科。")
    else:
        # 未选科目 → 整体推广，可用该年级全部科目。
        subjects = level_subjects
        focus_line = "- 未指定具体科目：整体推广该年级补习，自然提及最有代表性的 1-2 科即可，不必罗列全部。"

    rules = "\n".join("- " + r for r in COMPLIANCE_RULES["copy"])
    selling = "、".join(brief.get("coreSellingPoints", []))

    return f"""你是马来西亚顶级数字营销文案专家，专门为本地中小企业撰写「高点击率、高互动」的 Facebook 广告文案。

## 公司信息
- 公司：GENIUS SMK（Genius Secondary）
- 网站：geniussmk.com
- 行业：教育 Education
- 业务：{brief.get('whatTheyDo')}
- 核心卖点：{selling}

## 活动设置
- 目标：{obj}
- 类型：{mtype}
- 年级聚焦：{form_focus}
- 本级真实科目（只能提这些）：{subjects}
{focus_line}
- 语言：中文（必须简体华文）
- 平台：Facebook 信息流（必须）
- 适合「互动 / Engagement」与「转化」型广告：依「类型」决定 CTA 的软硬。

## 受众（重要）
- 对象是马来西亚华裔家长（孩子 13–17 岁中学生）。文案对「家长」说，绝不直接对孩子说，也不针对 18 岁以下投放。
- 初中（Form 1–3）没有 Add Math / 理科 / 商科，绝不为初中广告提这些科目。

## 平台风格指南（Facebook）
清楚直接、转化导向、适当 emoji、段落分明；CTA 用 WhatsApp / 私讯 / 链接。

## 成功案例参考（只学结构与 Hook 方式，内容必须 100% 原创，严禁抄袭）
{REFERENCE_HOOKS}

## 生成要求
1. 参考上面案例的成功结构与 Hook 方式，但内容 100% 原创。
2. 融入马来西亚本地文化与用语（地名如 KL / 柔佛 / 雪兰莪 / 槟城；本地语气词 lah、kan、jom），让家长觉得「这是本地人写的」。
3. 结构必须包含：强力 Hook → 核心卖点（分点更佳，可用 ✅）→ 社会证明 / 紧迫感（如名额有限）→ 明确 CTA。
4. 要有「成功广告的感觉」——让人想停下来、想留言、想私讯。
5. 正文（primaryText）写成一则完整、有感染力的 FB 帖文：第一行 Hook 必须在前 125 字内抓住眼球（手机「查看更多」前），但整段正文可以长、可分多段、可用符号列点。
6. Hook 用「很多家长…」「孩子一上中学…」这类共鸣场景，不要写「你的孩子很差 / 不及格」这种断定式（会被 Meta 判定为针对个人特征）。

## 合规（硬规则）
{rules}

## Facebook 字段目标
- Headline（标题）：约 {FB_SPECS['headline']['writeTo']} 字，最锋利的卖点或邀请。
- Description（描述，可选）：约 {FB_SPECS['description']['writeTo']} 字。
- CTA 按钮：从这些里选恰好一个（互动类优先 Send Message；转化类可 Send Message / Get Offer / Learn More）：{", ".join(FB_CTA_BUTTONS)}。

## 输出（只返回严格 JSON，不要任何说明或前缀）
{{
  "primaryText": "完整的 FB 长帖文，含 Hook、分点卖点、社会证明/紧迫感、CTA",
  "primaryTextVariations": ["另一种 Hook 角度的版本", "再一种"],
  "headline": "string",
  "headlineOptions": ["string", "string"],
  "description": "string",
  "cta": "从固定按钮里选一个",
  "creativeDirection": "一句话描述图片的核心视觉信息",
  "imageKeywords": ["3-6 个从本文案提炼的中文关键词，用于图片生成"]
}}
全部用简体中文，写给家长，主打马来西亚本地高互动 Facebook 广告。"""


# ---- Gate 2: the image prompt fed to gpt-image-2 ---------------------------
def build_image_prompt(brief, selections, writeup, matched=None):
    obj = _label(OBJECTIVES, selections["objective"])
    headline = (writeup.get("headline") or "").strip()
    subline = (writeup.get("description") or "").strip()
    keywords = writeup.get("imageKeywords") or []
    form_focus = selections.get("formDesc") or "Form 1 到 Form 5"
    rules = "\n".join("- " + r for r in COMPLIANCE_RULES["image"])

    kw_join = "、".join(keywords) if keywords else "（围绕文案标题与核心信息）"
    sub_line_block = f"- 可加一行更小的副标题（次要）：「{subline}」\n" if subline else ""

    return f"""Create a professional marketing advertisement image for a 教育 Education business named "GENIUS SMK" in Malaysia.

Platform: Facebook (feed, square 1:1)
Campaign objective: {obj}
Business: 线上中学补习（年级聚焦：{form_focus}）
受众: 马来西亚华裔家长（孩子 13–17 岁中学生）

核心视觉信息: {writeup.get('creativeDirection') or headline}
视觉关键词（必须围绕这些文案重点来构图与选取元素）: {kw_join}

Visual style references (style only, content must be original):
学生开心学习的明亮场景; 温馨专业的在家线上学习画面; 老师在屏幕上亲切讲解

Requirements:
- Modern, eye-catching, high-conversion ad visual
- Suitable for Facebook feed
- Vibrant colors, professional composition
- Malaysian context/elements where appropriate
- WORDING MUST FOLLOW THE WRITE-UP KEYWORDS（图上文字与元素必须呼应上面的视觉关键词）
- Clean, uncluttered composition, single clear focal point
- Lifestyle / product photography style

ON-IMAGE TEXT（必须出现在图片上，简体中文）:
- 把这句标题渲染为图片主视觉文字，大、醒目、清晰可读：
  「{headline}」
{sub_line_block}- 每个汉字都要与上面完全一致，不可改写、翻译或乱码。
- 文字不要遮住人脸，留出高对比的干净区域。层次分明：标题为主，副标题为辅。

图片合规（硬规则）:
{rules}

不要出现可辨识的真实人物；不要使用你无权使用的 logo / 商标。"""
