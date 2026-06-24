# ---------------------------------------------------------------------------
# LOCKED MODELS — required by the project owner. Do not silently swap these.
# Verified against OpenAI's model list (April 2026):
#   - gpt-5.4        : text / copy generation  (product name "ChatGPT-5.4")
#   - gpt-image-2    : image generation        (product name "ChatGPT Images 2.0")
# To pin an exact version in production, use a snapshot id, e.g.
#   IMAGE_MODEL = "gpt-image-2-2026-04-21"
# ---------------------------------------------------------------------------
WRITEUP_MODEL = "gpt-5.4"
IMAGE_MODEL = "gpt-image-2"
IMAGE_SIZE = "1024x1024"          # square, fits Facebook 1:1 feed
IMAGE_QUALITY = "high"            # gpt-image-2: low | medium | high

# ---------------------------------------------------------------------------
# FIXED BUSINESS — the system is built only for this tuition business.
# No website step; this brief is always used.
# ---------------------------------------------------------------------------
FIXED_BRIEF = {
    "summary": "Genius Secondary 是马来西亚的中学线上补习中心，专为 SMK 国中生（Form 1–Form 5）提供线上补习。",
    "whatTheyDo": "提供 Form 1 到 Form 5 的中学线上补习，全马名师授课，100% 线上教学，以学生为中心。",
    "productsServices": [
        "Form 1–Form 5 中学线上补习（按年级提供对应科目）",
        "初中（F1–F3）：基础科目；高中（F4–F5）：含 Add Math、理科、商科等选修",
        "全马名师授课",
    ],
    "targetCustomer": "马来西亚华裔家长，孩子是 13–17 岁的中学生（Form 1–Form 5）",
    "coreSellingPoints": ["全马名师授课", "100% 线上教学", "以学生为中心的教学方式", "涵盖 SMK 国中全科目"],
    "brandTone": "亲切、专业、鼓励",
    "industry": "education",
    "claimsSupportedOnSite": ["成立于 2018 年", "100% 线上教学", "提供免费试课", "全马名师阵容"],
    "language": "Simplified Chinese",
}

# ---------------------------------------------------------------------------
# User selections (Facebook is the only platform by design)
# ---------------------------------------------------------------------------
OBJECTIVES = [
    {"id": "acquisition", "label": "获取新客户"},
    {"id": "retention", "label": "拉复购 / 回购"},
    {"id": "awareness", "label": "提升品牌曝光"},
    {"id": "reviews", "label": "收集评价"},
]

MARKETING_TYPES = [
    {"id": "conversion", "label": "直接转化"},
    {"id": "seeding", "label": "种草推广"},
    {"id": "engagement", "label": "互动留存"},
]

# Form / year-group focus. "F" = Form. Lets the ad target a specific level or range.
FORM_LEVELS = [
    {"id": "f1", "label": "F1", "desc": "Form 1"},
    {"id": "f2", "label": "F2", "desc": "Form 2"},
    {"id": "f3", "label": "F3", "desc": "Form 3"},
    {"id": "f4", "label": "F4", "desc": "Form 4"},
    {"id": "f5", "label": "F5", "desc": "Form 5"},
    {"id": "f1_f3", "label": "F1–F3", "desc": "Form 1 到 Form 3（初中阶段）"},
    {"id": "f4_f5", "label": "F4–F5", "desc": "Form 4 到 Form 5（高中 / SPM 备考阶段）"},
    {"id": "f1_f5", "label": "F1–F5", "desc": "Form 1 到 Form 5（全阶段）"},
]

# Subjects available PER level. Lower secondary (F1-F3) does NOT have the
# upper-secondary electives (Add Math, Chemistry, Physics, Biology, Ekonomi, Akaun).
LOWER_SUBJECTS = "国文（BM）、英文、数学（Mathematics）、科学（Science）、历史（Sejarah）、Geografi"
UPPER_SUBJECTS = ("国文（BM）、英文、数学（Mathematics）、Add Math（高级数学）、"
                  "Physics、Chemistry、Biology、Sejarah、Ekonomi、Akaun（会计）")

# Subject groups for the picker (label = what the parent-facing UI shows).
BASIC_SUBJECTS = ["国文 BM", "英文", "数学", "科学", "历史 Sejarah", "Geografi"]
UPPER_SUBJECTS_LIST = ["Add Math", "Physics 物理", "Chemistry 化学", "Biology 生物",
                       "Ekonomi 经济", "Akaun 会计"]

# Which groups to SHOW for each form id.
def subject_groups_for(form_id):
    """Return list of (group_title, [subjects]) to display for the chosen form."""
    if form_id in ("f1", "f2", "f3", "f1_f3"):
        return [("基础科目", BASIC_SUBJECTS)]
    if form_id in ("f4", "f5", "f4_f5"):
        return [("基础科目", BASIC_SUBJECTS), ("高年级科目（F4–F5）", UPPER_SUBJECTS_LIST)]
    # f1_f5 → both groups
    return [("基础科目", BASIC_SUBJECTS), ("高年级科目（F4–F5）", UPPER_SUBJECTS_LIST)]

# Which subject set applies to each form id.
FORM_SUBJECTS = {
    "f1": LOWER_SUBJECTS, "f2": LOWER_SUBJECTS, "f3": LOWER_SUBJECTS, "f1_f3": LOWER_SUBJECTS,
    "f4": UPPER_SUBJECTS, "f5": UPPER_SUBJECTS, "f4_f5": UPPER_SUBJECTS,
    "f1_f5": ("初中（F1–F3）：" + LOWER_SUBJECTS + "；高中（F4–F5）：" + UPPER_SUBJECTS),
}

# ---------------------------------------------------------------------------
# Facebook ad field specs (2026). writeTo = target; hardCap = technical ceiling.
# ---------------------------------------------------------------------------
FB_SPECS = {
    "primaryText": {"writeTo": 125, "hardCap": 63206, "note": "前约 125 字会在手机上「查看更多」前显示，钩子放第一行"},
    "headline": {"writeTo": 27, "hardCap": 255, "note": "Facebook 信息流约显示 27 字，最锋利的卖点或优惠"},
    "description": {"writeTo": 30, "hardCap": 255, "note": "手机上常被隐藏，别放重要信息"},
}

# Facebook's fixed CTA buttons — pick ONE, never free text.
FB_CTA_BUTTONS = [
    "Shop Now", "Learn More", "Sign Up", "Book Now",
    "Get Offer", "Send Message", "Contact Us", "Subscribe",
]

# ---------------------------------------------------------------------------
# Layer 7 — Meta compliance guardrails (injected into prompts + post-checked)
# ---------------------------------------------------------------------------
COMPLIANCE_RULES = {
    "copy": [
        "不可暗示你了解观众或其孩子的特征（不要写「你的孩子成绩差吗」「专为很弱的学生」）。用利益导向、第三人称表达，让读者自行对号入座。",
        "不可保证成绩或用前后对比。真实见证只能作为「某位学生的个人经历」呈现，附「结果因人而异」，且不可放进标题。",
        "对象是家长 / 监护人，绝不直接对孩子说话，也不针对 18 岁以下投放。",
        "只陈述官网可佐证的内容（广告与落地页会被一并审核）。",
        "不要全大写喊叫、不要制造虚假紧迫、不要「100%」式保证。",
        "从固定的 Facebook 按钮列表中只选一个 CTA。",
    ],
    "image": [
        "不要前后对比的成绩 / 成绩单画面（暗示转变）。",
        "不要假界面 —— 不要假播放键、假关闭叉、假通知红点。",
        "不要可辨识的真实未成年人。用一般课堂 / 在家学习场景或插画。",
        "不要保证印章、不要「100%」徽章、不要惊悚画面。",
        "保持强层次、单一焦点；图上文字限定为广告标题加一行可选副标题。",
        "若为 AI 生成图片，请依 Meta 2026 规定标注。",
    ],
}

# Best-effort risk patterns (Python regex, re.IGNORECASE applied)
RISK_PATTERNS = {
    "personalAttribute": [r"\bare you\b", r"\bis your (child|kid|son|daughter)\b",
                          r"\bstruggling\b", r"\bweak (in|at)\b", r"\bfailing\b",
                          r"你的孩子", r"很差|很弱|不及格"],
    "guaranteedResult": [r"\bguarantee", r"\b100%\b", r"\bsure to\b", r"保证|包过|一定能"],
    "beforeAfter": [r"\bbefore\s*/?\s*after\b", r"\bfrom \d+\s*(to|→|->)\s*\d+", r"前后对比", r"从 ?\d+ ?分.*到 ?\d+ ?分"],
    "shouting": [r"\b[A-Z]{5,}\b"],
}
