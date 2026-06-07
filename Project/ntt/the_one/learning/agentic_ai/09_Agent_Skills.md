# 09 — Agent Skills (SKILL.md)

> Anthropic's open standard สำหรับ "ความรู้ + workflow ที่ agent โหลดได้ตามต้องการ"
> โครงสร้าง folder + markdown ที่ portable ข้าม Claude Code / Claude.ai / Claude API / และ agent platform อื่นๆ

---

## 1. Skill คืออะไร — และทำไมต้องมี

### นิยาม

> **Skill** = folder ที่บรรจุ instruction + script + reference สำหรับ agent ในรูปแบบ SKILL.md
> Agent **โหลด metadata ก่อน → โหลด content เต็มเมื่อจำเป็น** (progressive disclosure)

ตัวอย่าง folder:
```
my-skill/
├── SKILL.md          # required — frontmatter + instructions
├── scripts/
│   └── helper.py     # script (run, ไม่ load เข้า context)
└── reference/
    └── api.md        # reference (load เมื่อ agent อ่าน)
```

### History

- **Oct 2025**: Anthropic launch "Agent Skills" — beta feature
- **Dec 2025**: ประกาศเป็น **open standard** ที่ [agentskills.io](https://agentskills.io)
- **2026**: 30+ agent platform adopt (Cursor, Gemini CLI, OpenHands, GitHub Copilot, VS Code...)

→ Skill **ไม่ใช่** Claude-only แล้ว — เป็น cross-platform standard เหมือน MCP

### Motivation: ปัญหาที่ Skill แก้

ก่อน Skill — ถ้าอยากให้ agent ทำงานเฉพาะทาง:
- ใส่ใน system prompt → ใช้ context ทุกครั้ง แม้ไม่ได้ใช้
- Memory file (CLAUDE.md) → always-on, ใช้ context เปลือง
- Subagent → spawn process ใหม่
- Custom code → ไม่ portable

Skill ตอบโจทย์ทั้งหมด:
- โหลดเฉพาะ metadata (~100 token / skill) → มี 100 skill ก็ไม่ระเบิด context
- Content เต็มโหลดเมื่อ relevant
- Folder structure → version control ได้, share ได้
- Cross-product (Code, API, Apps)

---

## 2. SKILL.md Format

### 2.1 Minimal

```yaml
---
name: my-skill
description: What this skill does and when to use it
---

# Skill Title

Instructions for the agent...
```

แค่ 2 fields ก็พอ — `name` + `description`

### 2.2 Full Frontmatter (Claude Code)

```yaml
---
# Required
name: review-pr
description: Review GitHub pull requests, analyze changes, provide feedback. Use when user asks about PR review, change analysis, or wants to understand PR diffs.

# Optional — invocation control
when_to_use: Also triggered by "review code", "look at this PR"
disable-model-invocation: false      # Claude can auto-invoke?
user-invocable: true                  # show in /menu?

# Optional — arguments
argument-hint: "[pr-number]"
arguments: [pr_number]                # for $0, $1 substitution

# Optional — execution
allowed-tools: Bash(gh *)             # tools allowed without approval
model: claude-opus-4-7                # override session model
effort: high                          # override effort

# Optional — context isolation
context: fork                         # run in subagent
agent: Explore                        # which subagent

# Optional — conditional activation
paths:
  - "**/*.py"
  - "src/**"

# Optional — shell + hooks
shell: bash
hooks: {...}
---

# Pull Request Reviewer

Step 1: Run `gh pr view {{pr_number}} --json title,body,files`
Step 2: Read [REVIEW_GUIDE.md](REVIEW_GUIDE.md) for checklist
Step 3: Provide feedback in this format: ...
```

### 2.3 Constraints

| Field | Limit |
|---|---|
| `name` | ≤ 64 chars, lowercase + numbers + hyphens, no "claude"/"anthropic" |
| `description` | ≤ 1024 chars |
| `description` + `when_to_use` | ≤ 1536 chars combined |
| SKILL.md body | recommend ≤ 500 lines |

⚠️ Description = **สิ่งที่สำคัญที่สุด** — Claude ตัดสินใจจะ activate skill จาก description อย่างเดียว

---

## 3. Progressive Disclosure — ทำไม Skill ต้นทุนต่ำ

### 3 ระดับ loading

```
LEVEL 1: METADATA (always loaded, ~100 tokens / skill)
   └── name + description in system prompt

LEVEL 2: SKILL.md BODY (loaded when triggered, ~5K tokens)
   └── Full instructions injected to context

LEVEL 3: BUNDLED RESOURCES (loaded as needed, ~∞)
   ├── reference/*.md  → cat'd when needed
   ├── scripts/*.py    → executed (code NOT loaded), only stdout
   └── data/*.json     → read on demand
```

### ตัวอย่างเปรียบเทียบ

**Without Skills** (ทุก domain expertise ใน system prompt):
- 50 domain × 2K tokens = **100K tokens at startup** 😱

**With Skills** (progressive disclosure):
- 50 skills × 100 tokens metadata = **5K tokens at startup**
- + skill ที่ active (~5K)
- = ~10K tokens **only when used**

ลด context cost > 90%

### Compaction behavior

เมื่อ Claude Code auto-compact (context เต็ม):
- Skill content ใช้ shared budget 25K tokens
- Most recent invocation ของ skill จะถูก re-attach
- Skill เก่ากว่าอาจถูก drop

→ ถ้า skill หยุดทำงาน หลัง long session — re-invoke ผ่าน `/skill-name`

---

## 4. Skill Anatomy

### 4.1 What goes in a Skill folder

```
my-skill/
├── SKILL.md                 # required: frontmatter + instructions
├── REVIEW_GUIDE.md          # reference (one-level deep, recommended)
├── scripts/
│   ├── analyze.py           # executable (Python/shell/Node)
│   └── validate.sh
├── templates/
│   └── report.md            # template Claude fills in
├── data/
│   └── schema.json          # reference data
└── examples/
    └── sample_input.txt
```

### 4.2 How agent accesses each

| Type | How loaded | Token cost |
|---|---|---|
| **SKILL.md** | Auto when triggered | ~5K |
| **Reference (.md)** | Agent runs `cat reference.md` | size of file |
| **Scripts** | Agent runs `python scripts/x.py` | only stdout (code NOT loaded!) |
| **Data files** | Read by script or `cat` | depends |

→ **Scripts คือ pattern ที่ powerful ที่สุด**: deterministic logic ที่ไม่กิน context

### 4.3 Dynamic context (Claude Code only)

ใช้ ``!` `` ใน SKILL.md → run command **ก่อน** Claude เห็น content:

```markdown
# Current Status
!`git status --short`

# Recent commits
!`git log --oneline -10`

(Claude sees the command output, not the command)
```

### 4.4 Folder organization patterns

#### Pattern A: Single file skill
ง่ายๆ กรณีเล็ก
```
my-skill/SKILL.md
```

#### Pattern B: Skill + references
```
my-skill/
├── SKILL.md (overview + nav)
├── ADVANCED.md
├── EXAMPLES.md
└── REFERENCE.md
```

#### Pattern C: Domain-organized
```
api-skill/
├── SKILL.md
├── python/
│   ├── quickstart.md
│   └── examples.md
├── typescript/
│   ├── quickstart.md
│   └── examples.md
└── reference/
    ├── models.md
    ├── tools.md
    └── streaming.md
```

#### Pattern D: Skill + scripts
```
pdf-skill/
├── SKILL.md
└── scripts/
    ├── extract.py
    ├── merge.py
    └── fill_form.py
```

⚠️ **Avoid deep nesting** — 1 level deep ดี, 2 levels ก็ไหว, 3+ levels Claude อาจอ่านไม่ครบ

---

## 5. Locations & Precedence (Claude Code)

```
┌─────────────────────────────────────────────────────────┐
│  Enterprise (admin-managed)               highest prec  │
│  Personal (~/.claude/skills/)             ↓             │
│  Project (.claude/skills/)                ↓             │
│  Plugin (<plugin>/skills/)                lowest prec   │
└─────────────────────────────────────────────────────────┘
```

ถ้าชื่อ skill ซ้ำ — top เอาชนะ

### 5.1 Project-level (in repo)

```
my-project/
├── .claude/
│   └── skills/
│       ├── deploy/SKILL.md
│       └── review/SKILL.md
└── src/
```

✅ Commit ใน git → ทุกคนใน team auto-load
✅ Project-specific context

### 5.2 Personal

```
~/.claude/skills/
├── my-favorite/SKILL.md
└── another/SKILL.md
```

✅ ทุก project ใช้ได้
✅ Personal customization

### 5.3 Plugin

```
my-plugin/
├── .claude-plugin/plugin.json
└── skills/
    ├── skill-a/SKILL.md
    └── skill-b/SKILL.md
```

ติดตั้ง: `claude /plugin install github.com/user/my-plugin`

→ Distribution channel ที่ official ที่สุด

### 5.4 Skill Overrides (runtime control)

`.claude/settings.local.json`:
```json
{
  "skillOverrides": {
    "legacy-skill": "off",
    "verbose-skill": "name-only",
    "deploy-prod": "user-invocable-only"
  }
}
```

States:
- `"on"` — full visibility (default)
- `"name-only"` — name แต่ hide description
- `"user-invocable-only"` — Claude เห็นไม่ได้, user invoke ได้
- `"off"` — hidden เลย

---

## 6. Skills ใน Anthropic Products ต่างกันยังไง

### 6.1 Claude.ai (web/desktop apps)

- **Pre-built**: PowerPoint, Excel, Word, PDF — มาให้
- **Custom**: upload `.zip` ใน Settings → Features
- ⚠️ Per-user (ไม่ share workspace)
- ⚠️ ไม่มี filesystem access เต็ม

### 6.2 Claude Code

- **Filesystem-based** (full power)
- รองรับ all frontmatter fields
- Live change detection (edit SKILL.md → effect immediate)
- Plugin distribution

→ **ที่นี่คือบ้านจริงของ Skills**

### 6.3 Claude API

- Pre-built: `pptx`, `xlsx`, `docx`, `pdf` ผ่าน `container.skills`
- Custom: upload via `/v1/skills` endpoint (workspace-shared)
- จำกัด **8 skills/request**
- Custom skill upload size ≤ 30MB
- ต้อง beta header: `skills-2025-10-02`

```python
# API usage
response = client.beta.messages.create(
    model="claude-opus-4-7",
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [
            {"type": "anthropic", "skill_id": "pptx", "version": "latest"},
            {"type": "custom", "skill_id": "skill_01AbC...", "version": "latest"},
        ]
    },
    messages=[...],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)

# Upload custom skill
from anthropic.lib import files_from_dir

skill = client.beta.skills.create(
    display_title="Financial Analysis",
    files=files_from_dir("/path/to/skill_directory")
)
```

### 6.4 Comparison Table

| Feature | Claude.ai | Claude Code | Claude API |
|---|---|---|---|
| Pre-built skills | ✅ | ❌ | ✅ |
| Custom upload | ✅ (zip) | ✅ (filesystem) | ✅ (API) |
| Workspace sharing | ❌ | via plugin | ✅ |
| Conditional activation | limited | ✅ paths | limited |
| Subagent execution | ❌ | ✅ context:fork | limited |
| File bundling | ❌ | ✅ | ✅ |
| Versioning | manual | git | API |
| Live change detection | ❌ | ✅ | ❌ |

⚠️ **Skills ไม่ sync ข้าม product** — upload ไป Claude.ai ≠ ขึ้น API

---

## 7. ตัวอย่างจริง: PR Reviewer Skill

### 7.1 โครงสร้าง

```
~/.claude/skills/review-pr/
├── SKILL.md
├── REVIEW_GUIDE.md
├── STANDARDS.md
└── scripts/
    └── analyze_pr.py
```

### 7.2 SKILL.md

```yaml
---
name: review-pr
description: Review GitHub pull requests, analyze changes, and provide feedback. Use when user asks about PR review, change analysis, or wants to understand a PR.
allowed-tools: Bash(gh *)
context: fork
agent: Explore
arguments: [pr_number]
argument-hint: "[pr-number]"
---

# Pull Request Reviewer

Review changes in a GitHub pull request and provide actionable feedback.

## Step 1: Gather PR data

```bash
python ${CLAUDE_SKILL_DIR}/scripts/analyze_pr.py $0
```

## Step 2: Review against checklist

See [REVIEW_GUIDE.md](REVIEW_GUIDE.md) for full checklist (code quality, security, testing, docs).

## Step 3: Apply standards

See [STANDARDS.md](STANDARDS.md) for project code standards (Python/TS/general).

## Step 4: Output format

Provide feedback in this exact structure:

```markdown
## Summary
[1-2 sentences]

## Files Reviewed
- file.py: [assessment]

## Findings
- [issue with line ref]

## Suggestions
1. [actionable suggestion]

## Verdict: APPROVE / NEEDS CHANGES
```
```

### 7.3 REVIEW_GUIDE.md (separate file, loaded on demand)

```markdown
# PR Review Checklist

## Code Quality
- [ ] No obvious bugs
- [ ] Error handling present
- [ ] Clear names

## Security
- [ ] Input validation
- [ ] No SQL injection
- [ ] Dependencies up-to-date

## Testing
- [ ] New code has tests
- [ ] Edge cases covered

## Docs
- [ ] README updated if needed
```

### 7.4 scripts/analyze_pr.py

```python
#!/usr/bin/env python3
"""Analyze a GitHub PR. Output JSON."""
import subprocess, json, sys

def main(pr_num):
    pr = json.loads(subprocess.check_output(
        ["gh", "pr", "view", pr_num, "--json", "title,body,files,commits,author"],
        text=True
    ))
    diff = subprocess.check_output(["gh", "pr", "diff", pr_num], text=True)
    
    print(json.dumps({
        "pr": pr_num,
        "title": pr["title"],
        "files_changed": len(pr["files"]),
        "added_lines": diff.count("\n+"),
        "removed_lines": diff.count("\n-"),
        "file_types": list(set(f["path"].split(".")[-1] for f in pr["files"])),
    }, indent=2))

if __name__ == "__main__":
    main(sys.argv[1])
```

### 7.5 Usage

```bash
$ claude
> /review-pr 42

# Or auto-invoked:
> Please review PR 42 in my repo
```

Claude:
1. Reads SKILL.md → กระบวนการชัด
2. Runs `analyze_pr.py 42` → ได้ structured data (only stdout in context, ไม่มี script code)
3. Reads REVIEW_GUIDE.md เมื่อจำเป็น → checklist
4. Reads STANDARDS.md → กฎ project
5. Output formatted feedback

---

## 8. Distribution

### 8.1 Project (in-repo)

```bash
# Add skill to project
mkdir -p .claude/skills/my-skill
echo '---\nname: my-skill\ndescription: ...\n---\n# ...' > .claude/skills/my-skill/SKILL.md

# Commit
git add .claude/skills/
git commit -m "add team skill"
```

✅ ทุกคน clone repo → ได้ skill auto

### 8.2 Personal

```bash
mkdir -p ~/.claude/skills/my-fave
# ...
```

### 8.3 Plugin (best for sharing widely)

```
my-skill-pack/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── skill-a/SKILL.md
│   └── skill-b/SKILL.md
├── README.md
└── LICENSE
```

`plugin.json`:
```json
{
  "name": "my-skill-pack",
  "description": "Production-ready skills for X",
  "version": "1.0.0",
  "author": {"name": "..."},
  "homepage": "..."
}
```

Publish to GitHub → user install:
```bash
claude /plugin install github.com/user/my-skill-pack
```

✅ Versioned, namespaced (`/my-skill-pack:skill-a`), one-click

### 8.4 API workspace (programmatic)

```python
# Deploy skills via CI/CD
import anthropic
from anthropic.lib import files_from_dir

client = anthropic.Anthropic()

skill = client.beta.skills.create(
    display_title="Internal Reports",
    files=files_from_dir("./skills/reports/"),
)
print(f"Uploaded: {skill.id}")
```

GitHub Action ตัวอย่าง:
```yaml
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          pip install anthropic
          python scripts/upload_skills.py .claude/skills/
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 8.5 Anthropic's official skills

[github.com/anthropics/skills](https://github.com/anthropics/skills) — open source skills:
- Claude API skill (always-up-to-date API reference)
- + more

```bash
claude /plugin install anthropic/skills
```

---

## 9. Skills + MCP — How They Compose

ทั้งสองคนเป็น "augmentation layer" แต่คนละมุม:

| Aspect | Skill | MCP |
|---|---|---|
| Content | Instructions + scripts + refs | Tools + resources |
| Where | Local filesystem | Local OR remote server |
| What it does | Teaches "how to" | Provides "what can do" |
| Loading | Progressive (metadata first) | Tool schemas always loaded |
| State | Stateless | Can be stateful |

### Pattern: Skill that uses MCP tools

```yaml
---
name: database-analyzer
description: Analyze databases and generate reports. Use when querying data, analyzing schemas.
---

# Database Analysis

Use the BigQuery MCP tools to query data:

```
BigQuery:bigquery_schema(table="orders")
BigQuery:bigquery_query(query="SELECT ...")
```

For common queries see [QUERIES.md](QUERIES.md).
```

→ Skill = procedural knowledge + how-to-use
→ MCP = the actual tool execution

### Pattern: Plugin with both

```
my-data-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   └── data-analysis/SKILL.md     # how-to guide
└── .mcp.json                       # MCP server config
```

User install plugin → ได้ทั้ง skill (instructions) + MCP server (tools) → ใช้ร่วมกัน

### Decision

- **มี procedural knowledge ที่ reuse?** → Skill
- **มี tool/integration ใหม่ที่ต้อง expose?** → MCP
- **มีทั้งคู่?** → ใช้ทั้งคู่ใน plugin

---

## 10. Skill vs Alternatives — When to Use Each

### Decision tree

```
ต้องเพิ่มอะไรให้ agent?
   │
   ├── ความรู้/วิธีทำ procedure?
   │      │
   │      ├── สำคัญทุกครั้ง — never optional?
   │      │   └── SYSTEM PROMPT
   │      │
   │      ├── Project-specific facts?
   │      │   └── MEMORY (CLAUDE.md)
   │      │
   │      └── Domain expertise ที่ใช้บ้างไม่ใช้บ้าง?
   │          └── SKILL ★
   │
   ├── ความสามารถใหม่ (call API, run code)?
   │      │
   │      ├── External integration ที่ portable?
   │      │   └── MCP SERVER
   │      │
   │      └── In-app function?
   │          └── TOOL (function calling)
   │
   └── Reasoning context ที่แยกออก?
          └── SUBAGENT
```

### Comparison

| Aspect | Skill | System Prompt | Memory | Tool | MCP | Subagent |
|---|---|---|---|---|---|---|
| Always loaded | ❌ | ✅ | ✅ | schema only | schema only | ❌ |
| Token cost | 100/skill | full | full | low | low | full |
| Multi-file | ✅ | ❌ | ❌ | ❌ | ✅ resources | ✅ |
| Scripts | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Conditional activation | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Cross-product | ✅ standard | per app | per app | per LLM | ✅ standard | per app |

---

## 11. Pitfalls (เห็นคนทำผิดบ่อย)

### ❌ Description กว้างเกิน
```yaml
description: Helps with documents
```
Claude ไม่กล้า invoke เพราะไม่ชัดว่าใช้ตอนไหน

✅ ใส่ trigger keywords เฉพาะ:
```yaml
description: Generate quarterly financial reports from spreadsheet data. Use when user mentions "quarterly report", "financial analysis", "revenue breakdown".
```

### ❌ SKILL.md ใหญ่เกิน
ใส่ทุก doc ใน SKILL.md → 10K lines → ทุกครั้งที่ activate กิน 50K tokens

✅ Progressive disclosure:
- SKILL.md = overview + navigation (≤ 500 lines)
- ลึกๆ ไปอยู่ในไฟล์อื่น (load when needed)

### ❌ Reference nested ลึกเกิน
```
SKILL.md → see [a.md](a.md)
a.md → see [b.md](b.md)
b.md → see [c.md](c.md)  ← Claude อาจอ่านไม่ครบ
```

✅ Flat structure จาก SKILL.md

### ❌ Script ไม่ handle error
```python
def process(path):
    return open(path).read()  # FileNotFoundError → Claude งง
```

✅ Solve, don't punt:
```python
def process(path):
    if not os.path.exists(path):
        return ""  # graceful
    return open(path).read()
```

### ❌ Hardcoded paths
```markdown
Run: `python /Users/me/skills/my-skill/scripts/x.py`
```

✅ Use `${CLAUDE_SKILL_DIR}`:
```markdown
Run: `python ${CLAUDE_SKILL_DIR}/scripts/x.py`
```

### ❌ Time-sensitive info
```markdown
The current Claude model is Claude 3.7 Sonnet
```
จะเก่าใน 6 เดือน

✅ Generic:
```markdown
Use whichever Claude model is configured for the session.
```

### ❌ ไม่มี SKILL.md
```
my-skill/instructions.md  ← ไม่ใช่ SKILL.md → not detected
```

ชื่อต้องเป็น `SKILL.md` เป๊ะ (uppercase)

### ❌ Inconsistent terminology
ใช้ "API endpoint", "URL", "route" สลับกัน → Claude สับสน

✅ ใช้คำเดียวตลอด

---

## 12. Anti-pattern: ใส่ Skill เยอะเกิน

```
~/.claude/skills/
├── general-helper/
├── code-helper/
├── doc-helper/
├── ... (50 skills)
```

Discovery context จะเริ่มชน budget — Claude อาจไม่ activate skill ที่ตรง

✅ **Curate**:
- ถ้าไม่ใช้ใน 3 เดือน → ลบ
- ใช้ `skillOverrides` ตั้ง `"name-only"` สำหรับ rarely-used
- จัด plugin แยกตาม domain → install เฉพาะ domain ที่ทำงาน

---

## 13. Skills + Case Study (07) — Apply

ใน [Case Study e-commerce builder](07_Case_Study_Ecommerce_Builder.md), agents แต่ละตัว (Analyst, Architect, DBA, ...) **คือ candidate ของ Skill**:

```
my-builder/.claude/skills/
├── analyst/
│   ├── SKILL.md          # how to elicit requirements
│   └── QUESTIONS.md       # canonical question list
├── architect/
│   ├── SKILL.md
│   ├── PATTERNS.md        # arch patterns
│   └── scripts/draw_mermaid.py
├── dba-postgres/
│   ├── SKILL.md
│   ├── SCHEMA_RULES.md
│   └── scripts/validate_sql.py
├── reviewer/
│   ├── SKILL.md
│   └── CHECKLIST.md
└── ...
```

→ ใช้ใน Claude Code dev session ก็ได้ (developer ใช้ตัวเอง) + agent system production ก็ได้ (load via API)

ผลลัพธ์: skill ที่เขียนครั้งเดียว → ใช้ได้ทั้ง dev และ production

---

## 14. Tutorial: สร้าง Skill แรกของคุณ

### Step 1: Identify pattern
อะไรที่คุณบอก Claude ซ้ำๆ?
- "อย่าลืมเขียน type hint"
- "ทุก commit message ใช้ format นี้..."
- "ตอน review code ตรวจ X, Y, Z..."

→ พวกนี้ทุกตัวเป็น skill ได้

### Step 2: Scaffold

```bash
mkdir -p ~/.claude/skills/commit-style/
cd ~/.claude/skills/commit-style/
```

### Step 3: Write SKILL.md

```yaml
---
name: commit-style
description: Apply our team's commit message convention. Use when user asks to commit, write commit message, or stage changes for commit.
allowed-tools: Bash(git *)
---

# Commit Message Style

Our format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

## Examples

```
feat(auth): add OAuth2 login flow
fix(api): handle null response from /users
docs(readme): update setup instructions
```

## Rules

1. Subject ≤ 50 chars, imperative ("add" not "added")
2. Body wrapped at 72 chars
3. Reference issue: `Closes #123`

## Procedure

1. Run `git diff --staged` to see what changed
2. Pick correct type based on changes
3. Write message in our format
4. Confirm with user before commit
```

### Step 4: Test

```bash
cd /any/git/repo
echo "test" >> file.txt
git add file.txt
claude
> commit this
```

Claude should auto-invoke `commit-style` skill — เห็น log: `Activated skill: commit-style`

ถ้าไม่ activate:
- Description มี trigger keyword ที่ user พูดมั้ย?
- ลอง direct invoke: `/commit-style`

### Step 5: Iterate

ใช้จริง → เห็น Claude ตีความผิด → ปรับ SKILL.md
- Add example ที่ขาด
- Make description specific ขึ้น
- Add edge case rule

### Step 6: Share

Commit `~/.claude/skills/commit-style/` ไป personal dotfiles repo
หรือ build เป็น plugin → publish ให้ทีม

---

## 15. Comparison สรุป — Skills vs MCP vs CLAUDE.md

```
                    "How agent gets capability"
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐         ┌─────────┐         ┌─────────┐
   │ SKILL   │         │  MCP    │         │  TOOL   │
   │         │         │         │         │         │
   │ folder  │         │ server  │         │function │
   │ +.md    │         │ +schema │         │ schema  │
   │         │         │         │         │         │
   │ "how"   │         │ "what"  │         │ "what"  │
   │ proced. │         │ tool    │         │ tool    │
   │ guide   │         │portable │         │ inline  │
   └─────────┘         └─────────┘         └─────────┘


                  "What agent always knows"
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐         ┌─────────┐         ┌─────────┐
   │ SYSTEM  │         │ MEMORY  │         │  SKILL  │
   │ PROMPT  │         │ CLAUDE  │         │metadata │
   │         │         │ .md     │         │         │
   │ always  │         │ always  │         │ "names" │
   │ full    │         │ full    │         │ only    │
   └─────────┘         └─────────┘         └─────────┘
        │                   │                   │
        ▼                   ▼                   ▼
   high cost           high cost            low cost
   universal           project              optional
```

---

## 16. สรุป

- **Skill** = folder ที่บรรจุ instruction + scripts + refs ผ่าน SKILL.md
- **Progressive disclosure**: metadata → body → bundled resources (only when needed)
- เป็น **open standard** (Dec 2025) → portable ข้าม agent platform
- 3 ที่ที่อยู่: Claude Desktop / Code / API — ต่างกันใน distribution
- ดีที่สุดสำหรับ: domain expertise ที่ optional, procedure ที่ reuse, multi-file knowledge
- เริ่มต้นง่าย — `mkdir` + `SKILL.md` 5 บรรทัด ก็เริ่มได้
- Compose กับ MCP ดี — Skill = "how to use", MCP = "what to use"
- Anti-patterns: vague description, overstuffed SKILL.md, deep nesting

**ต่อไป**: ลองเขียน skill 1 ตัวสำหรับ pattern ที่คุณทำซ้ำๆ → จะเข้าใจมากขึ้น

---

## References

- [Agent Skills open standard](https://agentskills.io/) — spec
- [Claude Code Skills](https://code.claude.com/docs/en/skills.md) — official
- [Anthropic Skills repo](https://github.com/anthropics/skills) — official skills
- [Anthropic, "Introducing Agent Skills"](https://www.anthropic.com/news/skills) (Oct 2025)
- [Anthropic Engineering, "Equipping Agents for the Real World"](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Skills API guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide) — for Anthropic API
