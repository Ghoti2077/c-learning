#!/usr/bin/env python3
"""Obsidian 库体检 —— 每 5 次对话自动跑一次（由 agent 调用）

用法：
    python check_vault.py --tick    # 计数 +1；满 5 次才真正体检（平时几乎不输出，省 token）
    python check_vault.py           # 无条件体检
"""
import os, re, sys, glob

VAULT = r"D:\APP\hermes\c-learning"
STATE = os.path.join(VAULT, "_tools", ".tick")
EVERY = 5

def tick():
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    c = 0
    if os.path.exists(STATE):
        try:
            c = int((open(STATE, encoding="utf-8").read() or "0").strip())
        except Exception:
            c = 0
    c += 1
    if c >= EVERY:
        open(STATE, "w", encoding="utf-8").write("0")
        return True
    open(STATE, "w", encoding="utf-8").write(str(c))
    return False

def check():
    probs = []
    mds = glob.glob(os.path.join(VAULT, "**", "*.md"), recursive=True)
    names = {os.path.splitext(os.path.basename(p))[0] for p in mds}
    imgs = set(os.listdir(os.path.join(VAULT, "_附件"))) if os.path.isdir(os.path.join(VAULT, "_附件")) else set()

    for p in glob.glob(os.path.join(VAULT, "**", "*"), recursive=True):
        if not os.path.isfile(p):
            continue
        b = os.path.basename(p)
        rel = os.path.relpath(p, VAULT)
        if b.startswith("未命名") or b.startswith("~$"):
            probs.append(f"垃圾文件: {rel}")
        elif os.path.getsize(p) == 0:
            probs.append(f"空文件: {rel}")

    broken, miss_img = set(), set()
    for p in mds:
        t = open(p, encoding="utf-8", errors="ignore").read()
        # 去掉行内代码 `...` 和 ``` 代码块后再查，避免"文章里提到 <details> 这个词"被误判
        body = re.sub(r"```.*?```", "", t, flags=re.S)
        body = re.sub(r"`[^`\n]*`", "", body)
        if "<details>" in body:
            probs.append(f"HTML details 残留: {os.path.basename(p)}")
        for m in re.finditer(r"!\[\[([^\]\|]+)", t):
            if m.group(1).strip() not in imgs:
                miss_img.add(m.group(1).strip())
        for m in re.finditer(r"(?<!!)\[\[([^\]\|#]+)", t):
            tgt = m.group(1).strip().rstrip("\\").strip()   # 去掉表格里的 \| 别名转义残留
            if tgt.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".base", ".canvas", ".pdf")):
                continue
            if tgt not in names:
                broken.add(f"{os.path.basename(p)} → [[{tgt}]]")

    if miss_img:
        probs.append("缺图片: " + ", ".join(sorted(miss_img)))
    if broken:
        probs.append(f"断链 {len(broken)} 条: " + "; ".join(sorted(broken)[:5]))

    att = len([f for f in imgs])
    if probs:
        return "⚠️ 库体检发现 %d 个问题：\n- %s\n（共 %d 篇笔记 / %d 个附件）" % (len(probs), "\n- ".join(probs), len(mds), att)
    return "✅ 库体检通过（%d 篇笔记 / %d 个附件 / 0 问题）" % (len(mds), att)

def refresh_index():
    import make_index
    open(make_index.OUT, "w", encoding="utf-8").write(make_index.build())
    return make_index.OUT


if __name__ == "__main__":
    if "--tick" in sys.argv and not tick():
        print("·")          # 未到第 5 次，只吐一个点（省 token）
    else:
        msg = check()
        refresh_index()
        print(msg + " ｜ 首页已刷新")
