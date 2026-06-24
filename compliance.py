import re
from config import FB_SPECS, FB_CTA_BUTTONS, RISK_PATTERNS


def screen_copy(writeup):
    """Best-effort risk + length screen. Flags only — never auto-edits."""
    flags = []
    fields = {
        "正文": writeup.get("primaryText", "") or "",
        "标题": writeup.get("headline", "") or "",
        "描述": writeup.get("description", "") or "",
    }
    all_text = " \n ".join(fields.values())

    def check(patterns, msg):
        for p in patterns:
            if re.search(p, all_text, re.IGNORECASE):
                flags.append(msg)
                return

    check(RISK_PATTERNS["personalAttribute"], "可能含「针对个人特征」的表述（暗示了解观众或其孩子）。请改为利益导向。")
    check(RISK_PATTERNS["guaranteedResult"], "可能含「保证成绩」的说法。请软化；若用见证请加「结果因人而异」。")
    check(RISK_PATTERNS["beforeAfter"], "可能含「前后对比」框架。Meta 视为暗示转变，风险高。")
    check(RISK_PATTERNS["shouting"], "侦测到全大写。Meta 视为垃圾讯息，请用正常大小写。")

    # length checks
    counts = {}
    spec_map = {"正文": "primaryText", "标题": "headline", "描述": "description"}
    for name, val in fields.items():
        spec = FB_SPECS[spec_map[name]]
        if name == "正文":
            # Long primary text is fine; only the HOOK (first line) should fit before "see more".
            hook = (val or "").splitlines()[0] if val else ""
            hook_len = len(hook)
            counts[name] = {"len": len(val or ""), "target": spec["writeTo"], "over": False}
            if hook_len > spec["writeTo"]:
                flags.append(f"开头 Hook 有 {hook_len} 字，超过 {spec['writeTo']} 字，手机上可能在「查看更多」前被截断。")
        else:
            length = len(val)
            over = length > spec["writeTo"]
            counts[name] = {"len": length, "target": spec["writeTo"], "over": over}
            if over:
                flags.append(f"{name} 共 {length} 字，超过 {spec['writeTo']} 字目标，可能被截断。")

    cta = writeup.get("cta")
    if cta and cta not in FB_CTA_BUTTONS:
        flags.append(f"CTA「{cta}」不是有效的 Facebook 按钮。请从这些里选：{', '.join(FB_CTA_BUTTONS)}。")

    return {"flags": flags, "counts": counts, "pass": len(flags) == 0}
