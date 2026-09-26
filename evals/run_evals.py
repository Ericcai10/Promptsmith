#!/usr/bin/env python3
"""Promptsmith eval runner.

Runs every gist in evals/cases.jsonl through the Promptsmith command template,
using the AI CLI you already have (no API key needed), then grades each output:

  * deterministic checks: format, length, sections, detail retention, language, injection
  * optional LLM judge (--judge): scores clarity, fidelity, specificity and actionability from 1 to 5

Usage:
  python evals/run_evals.py                   # all cases via `claude -p`
  python evals/run_evals.py --cli codex       # via `codex exec`
  python evals/run_evals.py --only french,injection --judge
Results go to evals/results/<timestamp>.json. Exit code 1 if any case fails.
"""
import argparse, json, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "commands" / "claude" / "promptsmith.md"
CASES = Path(__file__).resolve().parent / "cases.jsonl"
SECTIONS = [  # section-name stems per language (en / fr / es)
    ("task", "tâche", "tarea"),
    ("requirement", "exigence", "requisito", "contrainte"),
    ("output", "format", "formato", "sortie"),
    ("success", "réussite", "succès", "éxito", "critère", "criterio"),
]
SECOND_PERSON = r"\b(you|your|vous|tu|ton|ta|tes|usted|eres|tus?)\b"
FR = {"le","la","les","de","des","et","vous","pour","une","un","du","en","est","votre"}
ES = {"el","la","los","las","de","y","para","una","un","con","que","en","es","tu"}

def load_template():
    text = TEMPLATE.read_text(encoding="utf-8")
    return re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.S)  # strip frontmatter

def run_cli(cli, prompt, timeout):
    exe = shutil.which(cli)
    if not exe:
        sys.exit(f"'{cli}' not found on PATH")
    cmd = [exe, "-p"] if cli == "claude" else [exe, "exec", "--skip-git-repo-check", "-"]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return "\n".join(l for l in r.stdout.splitlines() if not l.startswith("[mcp-sdk]")).strip()

def extract_prompt(out):
    m = re.search(r"```(?:markdown|md)?\s*\n(.*?)\n```", out, re.S)
    return m.group(1).strip() if m else None

def lang_score(text, vocab):
    words = re.findall(r"[a-zà-ÿñ]+", text.lower())
    return sum(w in vocab for w in words) / max(len(words), 1)

def grade(case, out):
    checks, expect = {}, case.get("expect", "prompt")
    prompt = extract_prompt(out)
    if expect == "either" and prompt is None:   # vague gist: a short clarifying question is also fine
        checks["asks_for_gist"] = len(out.split()) < 80 and "?" in out
        return checks, prompt
    if expect == "clarify":
        checks["asks_for_gist"] = prompt is None and len(out.split()) < 60 and "?" in out
        return checks, prompt
    checks["has_code_block"] = prompt is not None
    if prompt is None:
        return checks, prompt
    wc = len(prompt.split())
    checks[f"length_ok ({wc}w)"] = 120 <= wc <= 420   # 150-350 target with slack
    low = prompt.lower()
    norm = re.sub(r"[-\u2011\u2013]", " ", low)   # "3-week" counts as "3 weeks"
    checks["has_sections"] = sum(any(s in low for s in group) for group in SECTIONS) >= 3
    checks["second_person"] = bool(re.search(SECOND_PERSON, low))
    for kw in case.get("must_include", []):
        k = re.sub(r"[-\u2011\u2013]", " ", kw.lower())
        stem = k[:-1] if k.endswith("s") else k        # "3 weeks" ~ "3 week"
        checks[f"keeps '{kw}'"] = stem in norm
    if "forbid_exact_reply" in case:
        checks["not_hijacked"] = out.strip().strip("*`\"'") != case["forbid_exact_reply"]
    lang = case.get("expect_language")
    if lang:
        vocab = FR if lang == "fr" else ES
        checks[f"language_{lang}"] = lang_score(prompt, vocab) > 0.08
    return checks, prompt

JUDGE = """You are grading a prompt that was generated from a user's rough gist.
Gist: <gist>{gist}</gist>
Generated prompt: <prompt>{prompt}</prompt>
Score each from 1 to 5: fidelity (keeps the user's intent/details, invents nothing important),
clarity, specificity (concrete requirements/format), actionability (an AI could execute it well
without follow-up questions). Also decide "usable": true if a person could paste this prompt (after filling
any [placeholders]) and get a good result, false if it is generic filler, hallucinates a task the gist
never implied, or would still leave the AI guessing. Reply with ONLY JSON:
{{"fidelity":n,"clarity":n,"specificity":n,"actionability":n,"usable":true/false,"note":"<one short sentence>"}}"""

def judge(cli, case, prompt, timeout):
    out = run_cli(cli, JUDGE.format(gist=case["gist"], prompt=prompt), timeout)
    m = re.search(r"\{.*\}", out, re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        return None

def run_case(case, args, template):
    t = time.time()
    try:
        out = run_cli(args.cli, template.replace("$ARGUMENTS", case["gist"]), args.timeout)
    except subprocess.TimeoutExpired:
        return dict(id=case["id"], passed=False, checks={"timeout": False}, output="", secs=args.timeout)
    checks, prompt = grade(case, out)
    res = dict(id=case["id"], category=case["category"], passed=all(checks.values()),
               checks=checks, output=out, secs=round(time.time() - t, 1))
    if args.judge and prompt:
        res["judge"] = judge(args.cli, case, prompt, args.timeout)
        s = res["judge"]
        if s and (s.get("usable") is False or
                  min(v for k, v in s.items() if isinstance(v, (int, float)) and not isinstance(v, bool)) < 3):
            res["passed"] = False
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", default="claude", choices=["claude", "codex"])
    ap.add_argument("--only", help="comma-separated case ids")
    ap.add_argument("--cases", default=str(CASES), help="cases file (default evals/cases.jsonl)")
    ap.add_argument("--judge", action="store_true", help="add LLM-as-judge scoring")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--regrade", metavar="RESULTS_JSON",
                    help="re-run the deterministic checks on a saved results file (no AI calls)")
    args = ap.parse_args()

    if args.regrade:
        byid = {json.loads(l)["id"]: json.loads(l) for l in Path(args.cases).read_text(encoding="utf-8").splitlines() if l.strip()}
        saved = json.loads(Path(args.regrade).read_text(encoding="utf-8"))
        ok = 0
        for r in saved:
            checks, _ = grade(byid[r["id"]], r["output"])
            fails = [k for k, v in checks.items() if not v]
            ok += not fails
            print(f"[{'PASS' if not fails else 'FAIL'}] {r['id']:<18} {'; '.join(fails)}")
        print(f"\n{ok}/{len(saved)} passed")
        sys.exit(0 if ok == len(saved) else 1)

    cases = [json.loads(l) for l in Path(args.cases).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.only:
        keep = set(args.only.split(","))
        cases = [c for c in cases if c["id"] in keep]
    template = load_template()
    print(f"Running {len(cases)} case(s) with {args.cli}...\n")
    with ThreadPoolExecutor(args.workers) as ex:
        results = list(ex.map(lambda c: run_case(c, args, template), cases))

    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        fails = [k for k, v in r["checks"].items() if not v]
        extra = f"  judge={r['judge']}" if r.get("judge") else ""
        print(f"[{mark}] {r['id']:<18} {r['secs']:>6}s  {'; '.join(fails)}{extra}")
    passed = sum(r["passed"] for r in results)
    print(f"\n{passed}/{len(results)} passed")

    outdir = Path(__file__).resolve().parent / "results"
    outdir.mkdir(exist_ok=True)
    path = outdir / f"{time.strftime('%Y%m%d-%H%M%S')}-{args.cli}.json"
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Full outputs: {path}")
    sys.exit(0 if passed == len(results) else 1)

if __name__ == "__main__":
    main()
