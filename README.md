# ⚒️ Promptsmith

**Type the gist and get a real prompt back.**

Promptsmith is a slash command for **Claude Code** and **OpenAI Codex CLI**. You dump your half-formed thoughts into it, and the AI you're already using forges them into a clear, structured, **medium-length prompt** (~150–350 words) you can reuse anywhere.

No API keys, no dependencies. It's just a prompt file.

## Example

```
/promptsmith landing page for my french learning app, high schoolers, make it feel fun not school-y, nextjs + tailwind
```

↓ gives you something like:

```markdown
You are a senior frontend engineer and conversion-focused designer.

**Task:** Build a landing page for a free French-learning web app aimed at high school students...

**Requirements:**
- Next.js (App Router) + Tailwind CSS
- Playful, game-like tone. Avoid classroom/textbook aesthetics
- ...

**Output format:** ...
**Success criteria:** ...
```

It also lists any **assumptions** it made, so you can tweak them.

## Install

```bash
git clone https://github.com/Ericcai10/Promptsmith.git
cd Promptsmith
./install.sh            # both   (or: ./install.sh claude | ./install.sh codex)
```

Windows (PowerShell):
```powershell
.\install.ps1           # or: .\install.ps1 -Target claude
```

Or copy the file yourself:

| Tool | Copy this | To | Invoke with |
|---|---|---|---|
| Claude Code | `commands/claude/promptsmith.md` | `~/.claude/commands/` (global) or `.claude/commands/` (per project) | `/promptsmith <gist>` |
| Codex CLI | `commands/codex/promptsmith.md` | `~/.codex/prompts/` | `/prompts:promptsmith <gist>` |

Restart the CLI after you install.

## Customize

Edit the `.md` file to change the target length, the sections, or the tone. Both CLIs substitute `$ARGUMENTS` with whatever you type after the command.

## License

MIT
