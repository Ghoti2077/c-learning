#!/usr/bin/env python3
"""自动生成 Obsidian 库首页（总结索引）—— 让界面保持简洁

扫描库里所有课程笔记，抽取「标题 / 日期 / 一句话总结 / 状态」，
生成根目录的 🏠 C学习首页.md。可重复运行，每次覆盖。
"""
import os, re, glob

VAULT = r"D:\APP\hermes\c-learning"
OUT = os.path.join(VAULT, "🏠 C学习首页.md")
SKIP_DIRS = ("_附件", "_tools", ".obsidian", "_交接归档")
PROB_DIR = os.path.join("05-实战与考试", "题目")


def info(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    title = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r"^#\s+(.+)$", t, re.M)
    if m:
        title = m.group(1).strip()
    d = re.search(r"^-\s*日期：\s*(\S+)", t, re.M) or re.search(r"^date:\s*(\S+)", t, re.M)
    s = re.search(r"^>\s*\*\*一句话总结\*\*：\s*(.+)$", t, re.M)
    flag = ""
    if "🅿️ **状态：先放着" in t or "🅿️ **状态：预习" in t:
        flag = "🅿️ 预习"
    elif "✅ **已解决" in t:
        flag = "✅ 已解决"
    raw = s.group(1).strip() if s else ""
    raw = re.sub(r"\*\*|`|\*", "", raw)          # 去掉 ** 和 ` 等噪音
    raw = raw.replace("|", "\\|").replace("\n", " ")
    if len(raw) > 52:                              # 太长就截断，保持表格清爽
        raw = raw[:52].rstrip() + "…"
    return {
        "file": os.path.basename(path), "title": title,
        "date": d.group(1) if d else "", "sum": raw,
        "flag": flag,
    }


def natural_key(name):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", name)]


def build():
    rows, emb, tools, exams, probs = [], [], [], [], []
    for p in glob.glob(os.path.join(VAULT, "**", "*.md"), recursive=True):
        rel = os.path.relpath(p, VAULT)
        if any(rel.startswith(d) for d in SKIP_DIRS):
            continue
        base = os.path.basename(p)
        if base.startswith(("🏠", "❌", "📌", "_", "🧠")) or "草稿" in base:
            continue          # 草稿类（如 E09 帖子草稿）不算课
        i = info(p)
        if rel.startswith(PROB_DIR):
            probs.append(i)                       # 每题一页：只计数
        elif rel.startswith("05-嵌入式"):
            emb.append(i)                         # STM32 单独一区
        elif rel.startswith("05-"):
            exams.append(i)                       # 笔试、刷题总表等
        elif re.match(r"L\d+", base):
            rows.append(i)                        # C 语言课
        else:
            tools.append(i)
    rows.sort(key=lambda x: natural_key(x["file"]))
    emb.sort(key=lambda x: natural_key(x["file"]))
    tools.sort(key=lambda x: natural_key(x["file"]))
    exams.sort(key=lambda x: natural_key(x["file"]))
    probs.sort(key=lambda x: natural_key(x["file"]))

    L = []
    L.append("# 🏠 C 学习首页\n")
    errs = 0
    wp = os.path.join(VAULT, "❌ 我的易错点清单.md")
    if os.path.exists(wp):
        errs = len(re.findall(r"^\|\s*2026-", open(wp, encoding="utf-8").read(), re.M))
    todo = 0
    tp = os.path.join(VAULT, "📌 待办与欠账.md")
    if os.path.exists(tp):
        todo = len(re.findall(r"^- \[ \]", open(tp, encoding="utf-8").read(), re.M))
    L.append("> 自动生成的总结索引（每 5 次对话刷新一次）。**点标题进笔记，别在文件树里翻。**\n")
    L.append("**进度**：C 语言 %d 课 ｜ STM32 %d 课 ｜ 刷题 %d 题 ｜ 易错点 %d 条 ｜ 待办 %d 项 ｜ 附件 %d 张\n" % (
        len(rows), len(emb), len(probs), errs, todo,
        len(os.listdir(os.path.join(VAULT, "_附件"))) if os.path.isdir(os.path.join(VAULT, "_附件")) else 0))
    L.append("## 📚 C 语言课程笔记（%d 课）\n" % len(rows))
    L.append("| 课 | 日期 | 一句话总结 | 状态 |")
    L.append("|---|---|---|---|")
    for r in rows:
        name = r["file"][:-3]
        short = re.sub(r"\s*[（(].*$", "", name)
        L.append("| [[%s\\|%s]] | %s | %s | %s |" % (name, short, r["date"], r["sum"], r["flag"]))
    L.append("")

    if emb:
        L.append("## 🔌 嵌入式 · STM32（%d 课）\n" % len(emb))
        L.append("| 课 | 日期 | 一句话总结 | 状态 |")
        L.append("|---|---|---|---|")
        for r in emb:
            name = r["file"][:-3]
            short = re.sub(r"\s*[（(].*$", "", name)
            L.append("| [[%s\\|%s]] | %s | %s | %s |" % (name, short, r["date"], r["sum"], r["flag"]))
        L.append("")

    if exams:
        L.append("## 🎯 实战与考试（%d 篇）\n" % len(exams))
        for r in exams:
            L.append("- [[%s|%s]]：%s" % (r["file"][:-3], r["title"], r["sum"]))
        L.append("")
    L.append("## 🧩 刷题（做过的题各占一页）\n")
    L.append("- 🎯 [[🎯 刷题总表]] —— 题号 / 链接 / 状态 / 日期都在那张表里；题目页共 **%d** 页，点总表里的内链跳过去" % len(probs))
    L.append("")

    if tools:
        L.append("## 🛠 工具与排错\n")
        for r in tools:
            L.append("- [[%s|%s]]：%s" % (r["file"][:-3], r["title"], r["sum"]))
        L.append("")
    L.append("## 🧭 常用入口\n")
    L.append("- ❌ [[❌ 我的易错点清单]] —— 复习先看这张表")
    L.append("- 📌 [[📌 待办与欠账]] —— 欠着的作业 / 还没搞懂的问题")
    L.append("- 🎯 [[🎯 刷题总表]] —— 刷题主页（题号 / 链接 / 状态）")
    L.append("- 🧠 [[🧠 写代码的经验]] —— 动手前扫一眼的动作清单（踩过的坑都在上面）")
    L.append("- 🔁 [[📌 抽查池（间隔复习）]] —— 间隔复习登记处")
    L.append("- 🖼 `_附件/` —— 所有原始截图（课件 + VS 实测）")
    L.append("- 🔁 `_tools/check_vault.py` —— 库体检 + 刷新本页（每 5 次对话自动跑）")
    L.append("")
    L.append("## 📖 怎么用这个库（3 条）\n")
    L.append("1. **要看进度/找东西 → 就来这一页**，不用展开文件树")
    L.append("2. **复习 → 看 ❌ 易错点清单**（每日 8 点会有复习题）")
    L.append("3. **每课要点 → 点进笔记看「一句话总结」和「复习题讲评」两节**")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    txt = build()
    open(OUT, "w", encoding="utf-8").write(txt)
    print("已刷新 🏠 C学习首页.md（%d 行）" % txt.count("\n"))
