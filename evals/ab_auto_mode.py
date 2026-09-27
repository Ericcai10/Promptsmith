#!/usr/bin/env python3
"""Blind A/B test: does auto mode (the UserPromptSubmit hook) improve answers?

For each gist, runs `claude -p` in two throwaway folders, one with the hook
installed and one without. A judge then picks the better answer without
knowing which side had the hook. The A/B order is shuffled per case.

Usage: python evals/ab_auto_mode.py [--n 6]
"""
import argparse, json, os, random, re, shutil, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "promptsmith-auto.mjs"
GISTS = [
    "write a short product description for my handmade candles",
    "explain recursion to a beginner",
    "plan a cheap 3 day trip to chicago",
    "give me a study schedule for finals week",
    "write a python function to validate emails",
    "tips to make my tiktok account grow",
    "draft a text asking my boss for friday off",
    "make a workout plan for someone who hates running",
]
JUDGE = """A user typed this rough request to an AI assistant: <request>{g}</request>
Two assistants answered. Which answer serves the user better: more useful, better targeted to what they
probably meant, and appropriately complete without padding?
<answer_A>{a}</answer_A>
<answer_B>{b}</answer_B>
Reply with ONLY JSON: {{"winner":"A"|"B"|"tie","reason":"<one short sentence>"}}"""

CLAUDE = shutil.which("claude")

LIMIT = re.compile(r"session limit|usage limit|rate limit|hit your .*limit", re.I)

def ask(prompt, cwd):
    r = subprocess.run([CLAUDE, "-p"], input=prompt, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    out = "\n".join(l for l in r.stdout.splitlines() if not l.startswith("[mcp-sdk]")).strip()
    if not out or (LIMIT.search(out) and len(out) < 200):
        raise RuntimeError(f"CLI error: {out[:120] or '(empty output)'}")
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=len(GISTS))
    args = ap.parse_args()
    root = Path(tempfile.mkdtemp(prefix="ps-ab-"))
    on, off = root / "on", root / "off"
    (on / ".claude").mkdir(parents=True); off.mkdir()
    node = shutil.which("node").replace("\\", "/")
    cmd = f'"{node}" "{str(HOOK).replace(chr(92), "/")}"'
    (on / ".claude" / "settings.json").write_text(json.dumps(
        {"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": cmd, "timeout": 10}]}]}}))

    gists = GISTS[: args.n]
    with ThreadPoolExecutor(6) as ex:
        with_hook = list(ex.map(lambda g: ask(g, on), gists))
        without = list(ex.map(lambda g: ask(g, off), gists))
    # ask() raises on limit/empty output, so we only get here with real answers on both sides

    def judge(i):
        g, h, n = gists[i], with_hook[i], without[i]
        hook_is_a = random.random() < 0.5
        a, b = (h, n) if hook_is_a else (n, h)
        a = re.sub(r"^> ✨ Read as:.*\n+", "", a)   # hide the tell-tale line from the judge
        b = re.sub(r"^> ✨ Read as:.*\n+", "", b)
        try:
            out = ask(JUDGE.format(g=g, a=a, b=b), off)
            m = re.search(r"\{.*\}", out, re.S)
            v = json.loads(m.group(0)) if m else {}
        except Exception as e:
            v = {"reason": str(e)}
        w = v.get("winner")
        if w not in ("A", "B", "tie"):
            v["result"] = "error"          # never count a failed judgement as a win or loss
        else:
            v["result"] = "tie" if w == "tie" else ("hook" if (w == "A") == hook_is_a else "no-hook")
        return g, v, h.count("Read as")

    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(judge, range(len(gists))))
    tally = {"hook": 0, "no-hook": 0, "tie": 0, "error": 0}
    for g, v, fired in results:
        tally[v["result"]] = tally.get(v["result"], 0) + 1
        print(f"{v['result']:<8} hook_fired={bool(fired)}  {g}\n         {v.get('reason','')}")
    print("\n", tally)
    shutil.rmtree(root, ignore_errors=True)

if __name__ == "__main__":
    main()
