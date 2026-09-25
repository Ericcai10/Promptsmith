# Gold examples

Hand-written reference pairs showing what Promptsmith should produce. The first two are also embedded in the slash command as few-shot examples.

## 1. Everyday writing
**Gist:** `email my landlord about the broken heater its been 2 weeks, want it fixed asap + maybe a rent discount, dont want to sound rude`

```markdown
You are an assistant who helps tenants write clear, professional letters to their landlord.

**Task:** Write an email to my landlord asking them to repair the broken heater in my unit. It has been broken for two weeks. Also ask, politely, for a partial rent reduction for the period without heat.

**Requirements:**
- Keep the tone firm but friendly and respectful. It must not sound accusatory or rude.
- Say that the heater has not worked for 2 weeks and that the repair is now urgent.
- Ask for a specific next step: a repair visit within the next few days, with a confirmed date.
- Ask for the rent reduction as a reasonable request, not a demand, and suggest it covers the days without heat.
- Leave placeholders such as [Landlord name], [Unit number] and [date first reported] for details I haven't given.
- Don't cite specific laws or threaten action.

**Output format:** A subject line, then an email body of 150–220 words, signed with [My name]. After the email, add one alternative sentence I could use for a stronger tone if they don't reply.

**Success criteria:** The landlord knows exactly what's wrong, how long it has lasted, what I'm asking for and by when, and the email makes a good impression.
```
**Assumptions**
- No earlier written report is assumed, so the email includes a placeholder for when it was first reported.
- "Maybe a rent discount" is treated as a polite, optional request.

## 2. Coding
**Gist:** `python script that renames my photos by date taken, some dont have exif`

```markdown
You are an experienced Python developer who writes small, safe utility scripts.

**Task:** Write a Python script that renames the photos in a folder based on the date each one was taken, and handles photos that have no EXIF data.

**Requirements:**
- Read the capture date from EXIF `DateTimeOriginal` using Pillow. If it's missing, fall back to the file's modified time and log that the fallback was used.
- Use the filename format `YYYY-MM-DD_HH-MM-SS.ext`, keeping the original extension in lowercase.
- Avoid collisions: if two photos share a timestamp, add `_1`, `_2` and so on.
- Support `.jpg`, `.jpeg`, `.png` and `.heic` (skip HEIC with a warning if no HEIC reader is installed).
- Add a `--dry-run` flag that prints the planned renames without changing anything. Dry run is the default and `--apply` makes the changes.
- Take the folder path as a command-line argument (`argparse`). Don't recurse into subfolders unless `--recursive` is passed.

**Output format:** One complete `rename_photos.py` file, then a short "How to run" section with the install command and 2 example commands.

**Success criteria:** It runs on Windows/macOS/Linux, never overwrites or loses a file, and clearly reports which photos used the fallback date.
```
**Assumptions**
- Photos without EXIF fall back to the file's modified time.
- The script is non-destructive by default (dry run).
