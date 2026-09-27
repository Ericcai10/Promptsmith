#!/usr/bin/env python3
"""One-shot design bench for Promptsmith inside Hermes.

For each gist, runs three variants through `hermes chat -q --oneshot`, each in its own empty folder:
  off   : the raw gist, auto-mode hook disabled (PROMPTSMITH_AUTO=off)
  auto  : the raw gist, with the auto-mode hook
  forge : the gist is first forged into a prompt with the /promptsmith template, then that prompt is sent (hook off)
It then collects the HTML each run produced (a written file, or a ```html block in the reply) for rating.

Usage: python evals/oneshot_bench.py OUTDIR [--variants off,auto,forge] [--only id1,id2]
"""
import argparse, json, os, re, shutil, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = re.sub(r"^---.*?---\s*", "", (ROOT / "commands/claude/promptsmith.md").read_text(encoding="utf-8"), count=1, flags=re.S)
HERMES = shutil.which("hermes")
NOISE = re.compile(r"previous `hermes update`|Gateways may still|Run `hermes update`|^session_id:|Primary auth failed")

GISTS = {
    "button":    "make me an isolated button",
    "fashion":   "design a fashion website",
    "portfolio": "design a portfolio website",
    "pricing":   "make a pricing card section",
    "login":     "make a login page",
    "spinner":   "make a cool loading animation",
}
ONESHOT_SUFFIX = ("\n\n(One-shot: write a single self-contained HTML file to exactly this path: {path} . "
                  "Don't ask questions, don't use project context or memory; decide sensible defaults yourself.)")

def hermes(query, cwd, env_extra, turns=12):
    env = {**os.environ, **env_extra}
    t = time.time()
    r = subprocess.run([HERMES, "chat", "-q", query, "--oneshot", "-Q", "-t", "file", "--max-turns", str(turns)],
                       cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not NOISE.search(l)).strip()
    return out, round(time.time() - t)

def forge(gist, cwd):
    out, _ = hermes(TEMPLATE.replace("$ARGUMENTS", gist), cwd, {"PROMPTSMITH_AUTO": "off"}, turns=2)
    m = re.search(r"```(?:markdown|md)?\s*\n(.*?)\n```", out, re.S)
    return m.group(1).strip() if m else None, out

def collect_html(folder, reply):
    files = sorted(folder.rglob("*.html"), key=lambda p: p.stat().st_size, reverse=True)
    if files:
        return files[0].read_text(encoding="utf-8", errors="replace"), str(files[0].relative_to(folder))
    m = re.search(r"```html\s*\n(.*?)\n```", reply, re.S)
    return (m.group(1), "reply") if m else (None, None)

def run(job, outdir):
    gid, variant = job
    folder = outdir / f"{gid}-{variant}"
    shutil.rmtree(folder, ignore_errors=True); folder.mkdir(parents=True)
    gist = GISTS[gid]; forged = None
    if variant == "forge":
        forged, raw = forge(gist, folder)
        if not forged:
            return dict(id=gid, variant=variant, error="forge failed", reply=raw[:500])
        query, env = forged + ONESHOT_SUFFIX, {"PROMPTSMITH_AUTO": "off"}
    else:
        query = gist + ONESHOT_SUFFIX
        env = {"PROMPTSMITH_AUTO": "off" if variant == "off" else "show"}
    query = query.replace("{path}", str(folder / "index.html").replace("\\", "/"))
    reply, secs = hermes(query, folder, env)
    html, source = collect_html(folder, reply)
    if html:
        (folder / "_result.html").write_text(html, encoding="utf-8")
    return dict(id=gid, variant=variant, secs=secs, html_source=source, html_bytes=len(html or ""),
                read_as=(re.search(r"Read as:(.*)", reply) or [None, None])[1],
                asked_question=html is None and "?" in reply[-400:],
                forged_prompt=forged, reply=reply[:3000])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir"); ap.add_argument("--variants", default="off,auto,forge"); ap.add_argument("--only")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
    ids = a.only.split(",") if a.only else list(GISTS)
    jobs = [(g, v) for g in ids for v in a.variants.split(",")]
    with ThreadPoolExecutor(a.workers) as ex:
        results = list(ex.map(lambda j: run(j, outdir), jobs))
    (outdir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in results:
        print(f"{r['id']:<10} {r['variant']:<6} {r.get('secs','-'):>4}s html={r.get('html_bytes',0):>6}B "
              f"src={r.get('html_source')} asked={r.get('asked_question')} {r.get('error','')}")

if __name__ == "__main__":
    main()
