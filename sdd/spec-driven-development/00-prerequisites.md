# Machine Prerequisites — Spec-Driven Development Series

Everything here is **free tier**. Total setup time: ~20–30 minutes on a normal laptop (Windows, Mac, or Linux — even a basic 8GB RAM laptop works fine, no GPU needed).

## 1. A code editor — Visual Studio Code (Free)
- Download: https://code.visualstudio.com
- Works on Windows, macOS, Linux.

## 2. GitHub account (Free)
- Sign up: https://github.com
- You need this for GitHub Copilot's free tier.

## 3. GitHub Copilot — Free tier (this is our AI coding agent)
- Install the "GitHub Copilot" and "GitHub Copilot Chat" extensions inside VS Code (Extensions icon → search "GitHub Copilot" → Install).
- Sign in with your GitHub account when asked.
- GitHub gives a **free tier** (limited monthly "agent" requests) which is enough to follow this series. No credit card needed to start.
- Alternative free options (mention, don't have to demo all): Gemini CLI (free from Google), Claude Code (has a free trial). Spec Kit works with all of them — we'll use Copilot because it's the easiest free option for beginners.

## 4. Python (needed to install the Spec Kit CLI tool)
- Windows: https://python.org/downloads → check "Add Python to PATH" during install.
- Mac: `brew install python` (or python.org installer).
- Linux: usually pre-installed; else `sudo apt install python3`.
- Check install: open a terminal and type:
  ```
  python3 --version
  ```

## 5. `uv` — Python package runner (Free, this installs Spec Kit)
- This is what actually runs the `specify` command.
- Install (same command works on Mac/Linux terminal, or use the Windows PowerShell version from their docs):
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Windows PowerShell:
  ```
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- Check install:
  ```
  uv --version
  ```

## 6. Git (Free)
- Download: https://git-scm.com/downloads
- Check install:
  ```
  git --version
  ```

## 7. GitHub Spec Kit — the star of this series (Free, open source)
- This is the CLI tool that generates code from specs.
  ```
  uvx --from git+https://github.com/github/spec-kit.git specify init my-project
  ```

## Optional but nice to have
- A terminal you're comfortable with (VS Code's built-in terminal is enough — no separate app needed).
- Stable internet — Copilot and Spec Kit both need internet access (agent calls go to the cloud).

## Quick checklist
- [ ] VS Code installed
- [ ] GitHub account created
- [ ] GitHub Copilot extension installed + signed in
- [ ] Python installed
- [ ] `uv` installed
- [ ] Git installed

Once all boxes are checked, you're ready to follow along.