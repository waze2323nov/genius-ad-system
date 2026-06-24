# 精英广告系统（Streamlit 版）

中学线上补习（Form 1–Form 5）Facebook 广告生成器。流程：

```
活动选择  →  （可编辑）文案提示词  →  ChatGPT-5.4 生成文案
        →  （可编辑）图片提示词  →  gpt-image-2 生成图片  →  广告成品
```

- 业务已固定为 Genius Secondary 中学线上补习，**无需填写网站**。
- 受众锁定为 **13–17 岁学生及其家长**；文案全中文、互动 + 私讯导向。
- 系统自动抽取 `success_library.json` 里的 education 成功案例，注入两个提示词。
- 图片会把生成的**文案标题**渲染上去（gpt-image-2 对中文字渲染很强）。

## 锁定模型

`config.py` 里：

- 文案 `WRITEUP_MODEL = "gpt-5.4"`（即 ChatGPT-5.4）
- 图片 `IMAGE_MODEL = "gpt-image-2"`（即 ChatGPT Images 2.0）

要锁版本可改成快照：`IMAGE_MODEL = "gpt-image-2-2026-04-21"`。
首次调用 gpt-image-2 若提示需要验证，请到 platform.openai.com 后台完成 **Organization Verification**。

---

## 一、本地运行（先在自己电脑跑起来）

在项目文件夹打开 PowerShell，一行一行执行：

```powershell
pip install -r requirements.txt
```

填入 key（本地用 secrets 文件）：

```powershell
Copy-Item ".streamlit\secrets.toml.example" ".streamlit\secrets.toml"
notepad ".streamlit\secrets.toml"
```

把 `sk-在这里填入你的真实key` 换成你真实的 OpenAI key，存盘关闭。然后：

```powershell
streamlit run streamlit_app.py
```

浏览器会自动打开 `http://localhost:8501`。

> `secrets.toml` 已在 `.gitignore` 中，**不会**被上传到 GitHub。

---

## 二、上传 GitHub

1. 到 github.com 新建一个仓库（repository），例如 `genius-ad-system`（公开 Public 即可）。
2. 在项目文件夹的 PowerShell 里，一行一行执行（把 `你的用户名/genius-ad-system` 换成你的）：

```powershell
git init
git add .
git commit -m "Genius ad system - streamlit"
git branch -M main
git remote add origin https://github.com/你的用户名/genius-ad-system.git
git push -u origin main
```

> 因为 `.gitignore` 排除了 `secrets.toml`，你的 key 不会被推上去。推完后去 GitHub 仓库确认**看不到** `secrets.toml`。

---

## 三、部署到 Streamlit Community Cloud

1. 打开 share.streamlit.io，用 GitHub 登录。
2. 点 **New app** → 选你的仓库 `genius-ad-system`、分支 `main`、主文件 `streamlit_app.py`。
3. 点 **Advanced settings → Secrets**，粘贴：

```
OPENAI_API_KEY = "sk-你的真实key"
```

4. 点 **Deploy**。等一两分钟，就得到一个公开网址（`https://你的应用.streamlit.app`）。

以后你每次 `git push`，Streamlit Cloud 会自动重新部署。

---

## 四、填入你的成功广告（重要）

`success_library.json` 现在是两个 education 占位案例。把你 Google Drive 里的成功广告导出后，按文件里的格式补进去（记录**结构与视觉风格**，不是原文）。案例越多、越新，生成的文案越像「真正赢过的广告」。改完 `git push` 即可生效。

## 文件

| 文件 | 作用 |
|---|---|
| `streamlit_app.py` | 主程序（流程 + 两个可编辑关卡 + OpenAI 调用） |
| `config.py` | 锁定模型、固定业务、FB 规格、合规规则、选项 |
| `prompts.py` | 组装两个可编辑提示词 + 成功案例匹配 |
| `compliance.py` | 生成后合规风险与字数检查 |
| `success_library.json` | 成功广告参考库 |
| `.streamlit/secrets.toml` | 你的 key（本地，不上传） |

## 注意

- AI 生成图片上线前请依 Meta 2026 规定标注。
- 合规检查只是辅助提示，不代替人工审核，也不保证 Meta 必过。
- v1：单张成品、无历史记录、无登录。需要再加。
