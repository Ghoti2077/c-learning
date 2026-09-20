#!/usr/bin/env python3
"""自动生成 Obsidian 库首页（总结索引）—— 让界面保持简洁

扫描库里所有课程笔记，抽取「标题 / 日期 / 一句话总结 / 状态」，
生成根目录的 🏠 C学习首页.md。可重复运行，每次覆盖。
"""
import os, re, glob

VAULT = r"D:\APP\hermes\c-learning"
OUT = os.path.join(VAULT, "🏠 C学习首页.md")
SKIP_DIRS = ("_附件", "_tools", ".obsidian")


def info(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    title = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r"^#\s+(.+)$", t, re.M)
    if m:
        title = m.group(1).strip()
    d = re.search(r"^-\s*日期：\s*(\S+)", t, re.M)
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
    rows, tools = [], []
    for p in glob.glob(os.path.join(VAULT, "**", "*.md"), recursive=True):
        rel = os.path.relpath(p, VAULT)
        if any(rel.startswith(d) for d in SKIP_DIRS):
            continue
        if os.path.basename(p).startswith(("🏠", "❌", "📌")):
            continue
        i = info(p)
        (rows if re.match(r"L\d+", os.path.basename(p)) else tools).append(i)
    rows.sort(key=lambda x: natural_key(x["file"]))
    tools.sort(key=lambda x: natural_key(x["file"]))

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
    L.append("**进度**：已学 %d 课 ｜ 易错点 %d 条 ｜ 待办 %d 项 ｜ 附件 %d 张\n" % (
        len(rows), errs, todo,
        len(os.listdir(os.path.join(VAULT, "_附件"))) if os.path.isdir(os.path.join(VAULT, "_附件")) else 0))
    L.append("## 📚 课程笔记（%d 课）\n" % len(rows))
    L.append("| 课 | 日期 | 一句话总结 | 状态 |")
    L.append("|---|---|---|---|")
    for r in rows:
        name = r["file"][:-3]
        short = re.sub(r"\s*[（(].*$", "", name)
        L.append("| [[%s\\|%s]] | %s | %s | %s |" % (name, short, r["date"], r["sum"], r["flag"]))
    L.append("")
    if tools:
        L.append("## 🛠 工具与排错\n")
        for r in tools:
            L.append("- [[%s|%s]]：%s" % (r["file"][:-3], r["title"], r["sum"]))
        L.append("")
    L.append("## 🧭 常用入口\n")
    L.append("- ❌ [[❌ 我的易错点清单]] —— 复习先看这张表")
    L.append("- 📌 [[📌 待办与欠账]] —— 欠着的作业 / 还没搞懂的问题")
    L.append("- 📊 [[📊 学习看板.base]] —— 数据库视图（筛选 / 分组 / 统计，Obsidian 1.9+）")
    L.append("- 🗺️ [[🗺️ C语言知识地图.canvas]] —— 可视化学习路线（已学 → 下一站 → 嵌入式）")
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
