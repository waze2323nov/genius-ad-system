import base64
import json
import os

import streamlit as st
from openai import OpenAI

from config import (
    WRITEUP_MODEL, IMAGE_MODEL, IMAGE_SIZE, IMAGE_QUALITY,
    FIXED_BRIEF, OBJECTIVES, MARKETING_TYPES, FORM_LEVELS, FB_SPECS,
)
from config import subject_groups_for
from prompts import build_writeup_prompt, build_image_prompt
from compliance import screen_copy

st.set_page_config(page_title="精英广告系统 · Meta 广告生成", page_icon="📣", layout="wide")

# ----------------------------------------------------- playful FB desktop style
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&display=swap');

:root{ --fb:#1877F2; --fb2:#0866FF; --fb-dark:#0B5FCC; --gate:#F2A33C; --pop:#36C5F0; }

/* use Streamlit theme vars so Light / Dark / System all look right */
html, body, .stApp, [class*="css"]{ font-family:'Nunito',sans-serif !important; }
.stApp{ background:
  radial-gradient(1200px 600px at 72% -12%, rgba(54,197,240,.18), transparent 60%),
  var(--background-color); }
.block-container{ max-width:920px; padding-top:3.2rem; }
h1{ font-weight:900 !important; color:var(--text-color); letter-spacing:-.5px; }
h2,h3{ font-weight:800 !important; color:var(--text-color); }
p, label, span, div{ color:var(--text-color); }

/* Meta header banner */
.metabar{ background:linear-gradient(120deg,#1877F2 0%,#36C5F0 100%);
  border-radius:26px; padding:18px 24px; margin-bottom:20px;
  display:flex; align-items:center; gap:16px;
  box-shadow:0 12px 30px rgba(24,119,242,.30); }
.metabar .logo{ width:48px;height:48px;border-radius:16px;background:#fff;
  display:flex;align-items:center;justify-content:center;font-size:26px;
  box-shadow:0 6px 14px rgba(0,0,0,.12); }
.metabar .t{ font-size:21px;font-weight:900;line-height:1.15;color:#fff !important; }
.metabar .s{ font-size:13px;opacity:.95;color:#fff !important;font-weight:700; }

/* Cards */
.card{ background:var(--secondary-background-color);
  border:1.5px solid rgba(128,128,128,.18); border-radius:24px;
  padding:22px 24px; margin:16px 0; box-shadow:0 10px 26px rgba(22,38,61,.10); }
.bizbar{ background:rgba(24,119,242,.12); border:1.5px solid rgba(24,119,242,.32);
  border-radius:22px; padding:16px 20px; font-size:14px; font-weight:700;
  margin-bottom:10px; color:var(--text-color); }

.eyebrow{ font-size:12px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--fb) !important; font-weight:900; }
.eyebrow.gate{ color:var(--gate) !important; }
.section-label{ font-weight:800; font-size:15px; margin:14px 0 2px; color:var(--text-color); }
.fieldname{ font-size:13px; color:#8A93A3 !important; font-weight:800; }
.count{ font-family:'Nunito'; font-weight:800; font-size:12px; color:#8A93A3 !important; }
.count.over{ color:#E0455B !important; }
.val{ white-space:pre-wrap; font-size:15px; margin:4px 0 16px; color:var(--text-color); font-weight:600; }
.pill{ display:inline-block; font-size:13px; font-weight:800; background:var(--fb);
  color:#fff !important; padding:7px 16px; border-radius:999px;
  box-shadow:0 4px 10px rgba(24,119,242,.3); }

/* Buttons -> chunky rounded pills */
.stButton>button{ border-radius:999px !important; font-weight:800 !important;
  padding:.55rem 1.4rem !important; transition:transform .08s ease, box-shadow .12s ease; }
.stButton>button:hover{ transform:translateY(-1px); }
.stButton>button[kind="primary"]{ background:linear-gradient(120deg,#1877F2,#0866FF);
  border:none; color:#fff; box-shadow:0 10px 22px rgba(24,119,242,.35); }
.stButton>button[kind="primary"]:hover{ box-shadow:0 14px 28px rgba(24,119,242,.45); }
.stDownloadButton>button{ border-radius:999px !important; font-weight:800 !important; }

/* Pills */
[data-testid="stPills"] button{ border-radius:999px !important; font-weight:800 !important;
  padding:.4rem 1.1rem !important; }

/* Inputs */
textarea, input, [data-baseweb="input"]{ border-radius:16px !important; }
.stTextArea textarea{ border-radius:18px !important; font-size:14px; }

/* Sidebar */
section[data-testid="stSidebar"]{ border-right:1px solid rgba(128,128,128,.18); }
.metaword{ font-family:'Nunito';font-weight:900; font-size:30px;
  background:linear-gradient(120deg,#1877F2,#36C5F0);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent; line-height:1; }
.brandname{ font-size:15px; font-weight:900; color:var(--text-color); margin-top:4px; }
.brandsub{ font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:#8A93A3 !important; font-weight:800; }
.railitem{ padding:9px 12px; margin:4px 0; font-size:14px; font-weight:800; color:#9AA7BC;
  border-radius:14px; }
.railitem.active{ color:#fff !important; background:linear-gradient(120deg,#1877F2,#36C5F0);
  box-shadow:0 6px 14px rgba(24,119,242,.3); }
.railitem.active *{ color:#fff !important; }
.railitem.done{ color:var(--fb) !important; background:rgba(24,119,242,.12); }
.modeltag{ font-family:'Nunito'; font-weight:700; font-size:11px; color:#8A93A3 !important; }
</style>
""", unsafe_allow_html=True)

STAGES = [
    ("selections", "活动选择"),
    ("gate1", "文案提示词（可编辑）"),
    ("writeup", "文案生成 · ChatGPT-5.4"),
    ("gate2", "图片提示词（可编辑）"),
    ("output", "广告成品"),
]


def init():
    ss = st.session_state
    ss.setdefault("step", "selections")
    for k in ("objective", "marketingType", "formId", "formDesc", "subjects", "writeup", "compliance", "image_bytes"):
        ss.setdefault(k, None)
    ss.setdefault("writeup_prompt", "")
    ss.setdefault("image_prompt", "")
init()


def get_client():
    key = st.secrets.get("OPENAI_API_KEY", None) if hasattr(st, "secrets") else None
    if not key:
        key = os.environ.get("OPENAI_API_KEY")
    if not key:
        st.error("找不到 OPENAI_API_KEY。本地请在 .streamlit/secrets.toml 填入；Streamlit Cloud 请在 App settings → Secrets 填入。")
        st.stop()
    return OpenAI(api_key=key)


def explain_error(err):
    msg = str(err); low = msg.lower()
    if "model" in low and ("not found" in low or "does not exist" in low or "invalid" in low):
        return f"OpenAI 拒绝了模型：{msg}。请检查 config.py 里的 WRITEUP_MODEL / IMAGE_MODEL。"
    if "verification" in low or "verify" in low:
        return f"调用 gpt-image-2 可能需要先在 OpenAI 后台完成组织验证（Organization Verification）。原始信息：{msg}"
    if "api key" in low or "authentication" in low or "401" in low:
        return "OpenAI 身份验证失败。请检查你的 OPENAI_API_KEY。"
    if "insufficient" in low or "quota" in low or "billing" in low:
        return "OpenAI 额度 / 账单问题。请到 platform.openai.com 的 Billing 充值后再试。"
    return msg


def safe_json(text):
    try:
        return json.loads(text)
    except Exception:
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1:
            try:
                return json.loads(text[s:e + 1])
            except Exception:
                return None
    return None


def go(step):
    st.session_state.step = step
    st.rerun()


def pick(label, options):
    """Rounded pill selector, falling back to horizontal radio on older Streamlit."""
    if hasattr(st, "pills"):
        return st.pills(label, options, selection_mode="single", label_visibility="collapsed")
    return st.radio(label, options, index=None, horizontal=True, label_visibility="collapsed")


def pick_multi(options, key):
    """Multi-select rounded pills, falling back to multiselect on older Streamlit."""
    if hasattr(st, "pills"):
        return st.pills(key, options, selection_mode="multi", label_visibility="collapsed", key=key) or []
    return st.multiselect(key, options, label_visibility="collapsed", key=key)


def metabar(title, sub):
    st.markdown(
        f"<div class='metabar'><div class='logo'>📣</div>"
        f"<div><div class='t'>{title}</div><div class='s'>{sub}</div></div></div>",
        unsafe_allow_html=True,
    )


def sidebar():
    with st.sidebar:
        st.markdown("<div class='metaword'>Meta</div>"
                    "<div class='brandname'>精英广告系统</div>"
                    "<div class='brandsub'>Facebook · 效果导向</div>", unsafe_allow_html=True)
        st.divider()
        cur = st.session_state.step
        idx = [s[0] for s in STAGES].index(cur)
        for i, (sid, label) in enumerate(STAGES):
            cls = "active" if sid == cur else ("done" if i < idx else "")
            mark = "●" if sid == cur else ("✓" if i < idx else "○")
            st.markdown(f"<div class='railitem {cls}'>{mark}　{label}</div>", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<span class='modeltag'>文案：{WRITEUP_MODEL}　图片：{IMAGE_MODEL}</span>",
                    unsafe_allow_html=True)


def field_out(name, val, target=None):
    length = len(val or "")
    over = target and length > target
    cnt = f"<span class='count {'over' if over else ''}'>{length}{(' / ' + str(target)) if target else ''}</span>"
    st.markdown(f"<span class='fieldname'>{name}</span> {cnt}", unsafe_allow_html=True)
    st.markdown(f"<div class='val'>{(val or '').replace('<','&lt;')}</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------- steps
def step_selections():
    metabar("Meta 广告生成 ✨", "Facebook 信息流 · 中学线上补习")
    st.markdown("<span class='eyebrow'>第 1 步</span>", unsafe_allow_html=True)
    st.title("活动选择 🎯")
    st.write("选择年级聚焦、活动目标与营销类型。系统会自动抽取 education 成功案例，结合固定业务生成文案。")
    st.markdown(
        "<div class='bizbar'>🎓 <b>本系统专为：</b>Genius Secondary · 中学线上补习（Form 1–Form 5）｜"
        "<b>对象：</b>13–17 岁中学生及其家长。业务已固定，无需填写网站。</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-label'>📚 年级聚焦（F = Form）</div>", unsafe_allow_html=True)
    form_choice = pick("年级聚焦", [f["label"] for f in FORM_LEVELS])
    chosen_subjects = []
    if form_choice:
        _fobj = next(f for f in FORM_LEVELS if f["label"] == form_choice)
        st.caption("已选：" + _fobj["desc"])
        st.markdown("<div class='section-label'>📖 科目（可多选；不选 = 整体推广）</div>", unsafe_allow_html=True)
        for _gi, (_title, _subs) in enumerate(subject_groups_for(_fobj["id"])):
            st.markdown(f"<span class='fieldname'>{_title}</span>", unsafe_allow_html=True)
            chosen_subjects += pick_multi(_subs, key=f"subj_{_fobj['id']}_{_gi}")

    st.markdown("<div class='section-label'>🚀 活动目标</div>", unsafe_allow_html=True)
    obj_choice = pick("活动目标", [o["label"] for o in OBJECTIVES])

    st.markdown("<div class='section-label'>💡 营销类型</div>", unsafe_allow_html=True)
    type_choice = pick("营销类型", [m["label"] for m in MARKETING_TYPES])

    st.markdown("<div class='section-label'>📱 平台</div>", unsafe_allow_html=True)
    st.markdown("<span class='pill'>Facebook 信息流 · 已锁定</span>", unsafe_allow_html=True)
    st.write("")

    ready = bool(form_choice and obj_choice and type_choice)
    if st.button("生成文案提示词 →", type="primary", disabled=not ready):
        st.session_state.objective = next(o["id"] for o in OBJECTIVES if o["label"] == obj_choice)
        st.session_state.marketingType = next(m["id"] for m in MARKETING_TYPES if m["label"] == type_choice)
        fobj = next(f for f in FORM_LEVELS if f["label"] == form_choice)
        st.session_state.formId, st.session_state.formDesc = fobj["id"], fobj["desc"]
        st.session_state.subjects = chosen_subjects
        st.session_state.writeup_prompt = build_writeup_prompt(
            FIXED_BRIEF,
            {"objective": st.session_state.objective, "marketingType": st.session_state.marketingType,
             "formId": st.session_state.formId, "formDesc": st.session_state.formDesc,
             "subjects": st.session_state.subjects},
        )
        go("gate1")


def step_gate1():
    metabar("Meta 广告生成 ✍️", "可编辑提示词 · 文案")
    st.markdown("<span class='eyebrow gate'>可编辑环节 1</span>", unsafe_allow_html=True)
    st.title("检查文案提示词")
    st.write("以下就是将发送给 **ChatGPT-5.4** 的内容，已包含固定业务、年级聚焦与 education 成功案例结构。可任意编辑。")
    prompt = st.text_area("文案提示词", value=st.session_state.writeup_prompt, height=420, key="wp_edit")
    c1, c2 = st.columns([1, 4])
    if c1.button("← 返回"):
        go("selections")
    if c2.button("生成文案 · ChatGPT-5.4", type="primary"):
        st.session_state.writeup_prompt = prompt
        client = get_client()
        try:
            with st.spinner("ChatGPT-5.4 撰写中…"):
                resp = client.chat.completions.create(
                    model=WRITEUP_MODEL,
                    messages=[
                        {"role": "system", "content": "你是资深 Facebook 广告文案。只返回严格的 JSON。"},
                        {"role": "user", "content": prompt},
                    ],
                )
            writeup = safe_json(resp.choices[0].message.content or "")
            if not writeup:
                st.error("模型没有返回有效 JSON。请编辑提示词后重试。")
                return
            st.session_state.writeup = writeup
            st.session_state.compliance = screen_copy(writeup)
            go("writeup")
        except Exception as e:
            st.error(explain_error(e))


def step_writeup():
    w = st.session_state.writeup
    c = st.session_state.compliance
    sp = FB_SPECS
    metabar("Meta 广告生成 📝", "文案成品 · ChatGPT-5.4")
    st.markdown("<span class='eyebrow'>第 2 步</span>", unsafe_allow_html=True)
    st.title("已生成文案 🎉")
    st.markdown("<span class='modeltag'>模型：ChatGPT-5.4 ｜ 目标：最大化互动与私讯</span>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    field_out("正文", w.get("primaryText"), sp["primaryText"]["writeTo"])
    field_out("标题", w.get("headline"), sp["headline"]["writeTo"])
    field_out("描述", w.get("description"), sp["description"]["writeTo"])
    st.markdown(f"行动按钮　<span class='pill'>{w.get('cta','')}</span>", unsafe_allow_html=True)
    st.markdown("<span class='fieldname'>视觉方向（交给图片步骤）</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='val'>{(w.get('creativeDirection') or '')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if (w.get("primaryTextVariations") or w.get("headlineOptions")):
        with st.expander("备选方案"):
            for i, t in enumerate(w.get("primaryTextVariations") or []):
                field_out(f"正文 — 备选 {i+1}", t, sp["primaryText"]["writeTo"])
            for i, t in enumerate(w.get("headlineOptions") or []):
                field_out(f"标题备选 {i+1}", t, sp["headline"]["writeTo"])

    if c["flags"]:
        st.warning(f"合规检查 — 需要留意（{len(c['flags'])}）：\n\n" + "\n".join("• " + f for f in c["flags"]))
    else:
        st.success("合规检查通过 ✅ 发布前仍请人工再看一遍。")

    c1, c2 = st.columns([1, 4])
    if c1.button("← 重新编辑提示词"):
        go("gate1")
    if c2.button("生成图片提示词 →", type="primary"):
        st.session_state.image_prompt = build_image_prompt(
            FIXED_BRIEF,
            {"objective": st.session_state.objective, "marketingType": st.session_state.marketingType,
             "formId": st.session_state.formId, "formDesc": st.session_state.formDesc,
             "subjects": st.session_state.subjects},
            w,
        )
        go("gate2")


def step_gate2():
    metabar("Meta 广告生成 🎨", "可编辑提示词 · 图片")
    st.markdown("<span class='eyebrow gate'>可编辑环节 2</span>", unsafe_allow_html=True)
    st.title("检查图片提示词")
    st.write("以下就是将发送给 **gpt-image-2** 的内容。系统会把生成的**文案标题**渲染到图片上，并带上图片合规规则。可自由编辑。")
    prompt = st.text_area("图片提示词", value=st.session_state.image_prompt, height=420, key="ip_edit")
    c1, c2 = st.columns([1, 4])
    if c1.button("← 返回"):
        go("writeup")
    if c2.button("生成图片 · gpt-image-2", type="primary"):
        st.session_state.image_prompt = prompt
        client = get_client()
        try:
            with st.spinner("gpt-image-2 生成中…（复杂提示可能需要最长 2 分钟）"):
                resp = client.images.generate(
                    model=IMAGE_MODEL, prompt=prompt, size=IMAGE_SIZE, quality=IMAGE_QUALITY,
                )
            b64 = resp.data[0].b64_json
            if b64:
                st.session_state.image_bytes = base64.b64decode(b64)
                go("output")
            else:
                st.error("没有取得图片数据。请重试或编辑提示词。")
        except Exception as e:
            st.error(explain_error(e))


def step_output():
    w = st.session_state.writeup
    sp = FB_SPECS
    metabar("Meta 广告生成 🚀", "广告成品 · 可直接投放")
    st.markdown("<span class='eyebrow'>第 3 步</span>", unsafe_allow_html=True)
    st.title("✅ 全部生成完成")

    # 业务摘要
    obj = next((o["label"] for o in OBJECTIVES if o["id"] == st.session_state.objective), "")
    mtype = next((m["label"] for m in MARKETING_TYPES if m["id"] == st.session_state.marketingType), "")
    subs = "、".join(st.session_state.subjects) if st.session_state.subjects else "整体推广（未指定科目）"
    with st.expander("📋 业务摘要", expanded=True):
        st.markdown(
            f"- **公司：** GENIUS SMK（Genius Secondary）\n"
            f"- **行业：** 教育 Education\n"
            f"- **目标：** {obj}　·　**类型：** {mtype}\n"
            f"- **年级聚焦：** {st.session_state.formDesc or ''}\n"
            f"- **科目：** {subs}\n"
            f"- **平台：** Facebook　·　**语言：** 中文"
        )

    st.write("文案 + 图片，可直接放入广告管理工具。请依 Meta 2026 规定标注 AI 生成图片。")
    if st.session_state.image_bytes:
        st.image(st.session_state.image_bytes, width=420)
        st.download_button("⬇ 下载图片", st.session_state.image_bytes, "genius_ad.png", "image/png")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    field_out("正文", w.get("primaryText"), sp["primaryText"]["writeTo"])
    field_out("标题", w.get("headline"), sp["headline"]["writeTo"])
    field_out("描述", w.get("description"), sp["description"]["writeTo"])
    st.markdown(f"行动按钮　<span class='pill'>{w.get('cta','')}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<span class='modeltag'>文案：ChatGPT-5.4 · 图片：gpt-image-2</span>", unsafe_allow_html=True)

    full = (f"正文：\n{w.get('primaryText','')}\n\n标题：\n{w.get('headline','')}\n\n"
            f"描述：\n{w.get('description','')}\n\n行动按钮：{w.get('cta','')}")
    st.text_area("复制全部文案", value=full, height=160)

    if st.button("＋ 新建广告", type="primary"):
        for k in ("writeup", "compliance", "image_bytes", "objective", "marketingType", "formId", "formDesc", "subjects"):
            st.session_state[k] = None
        st.session_state.writeup_prompt = ""
        st.session_state.image_prompt = ""
        go("selections")


# ---------------------------------------------------------------- router
sidebar()
{
    "selections": step_selections,
    "gate1": step_gate1,
    "writeup": step_writeup,
    "gate2": step_gate2,
    "output": step_output,
}[st.session_state.step]()
