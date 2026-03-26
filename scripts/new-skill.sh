#!/usr/bin/env bash
# Scaffold a new Alpha Stack skill directory with SKILL.md template and prompts/
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <skill-name>"
  echo "Example: $0 fixed-income"
  exit 1
fi

NAME="$1"
DIR="skills/$NAME"

if [ -d "$DIR" ]; then
  echo "Error: $DIR already exists"
  exit 1
fi

mkdir -p "$DIR/prompts"
touch "$DIR/prompts/.gitkeep"

cat > "$DIR/SKILL.md" << 'TEMPLATE'
---
name: SKILL_NAME
description: >
  One-line description of what this skill does and when it activates.
---

# SKILL_NAME

## What I Do

I am a [role description]. I think in terms of [key frameworks].

## Scope & Boundaries

**What this skill does:**
- [Capability 1]
- [Capability 2]
- [Capability 3]

**Use a different skill when:**
- [Redirect condition] → `/other-skill`

## Pre-Flight Checks

Before starting, confirm:
1. [Required input 1]
2. [Required input 2]
3. [Required input 3]

## Phase 1: [Name]

**Goal:** [What this phase accomplishes]

### Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Decision Gate:** [What must be true to proceed]

## Phase 2: [Name]

**Goal:** [What this phase accomplishes]

### Steps
1. [Step 1]
2. [Step 2]

**Decision Gate:** [What must be true to proceed]

## Tool Integration

| When you need... | Run this tool |
|-----------------|---------------|
| [Analysis type] | `python3 tools/[tool].py` |

## Output Specifications

Primary deliverables:
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

## Quality Gates

- [ ] All assumptions listed explicitly
- [ ] Sensitivity analysis included
- [ ] Risk caveats documented
- [ ] No hallucinated numbers

## Hard Constraints

- **NEVER** fabricate financial data
- **NEVER** present a single-point estimate without a range
- **ALWAYS** include what kills the thesis

## Common Pitfalls

1. [Anti-pattern 1]
2. [Anti-pattern 2]

## Related Skills

- `/skill-1` — [when to use instead]
- `/skill-2` — [complementary analysis]
TEMPLATE

# Replace placeholder with actual skill name
sed -i '' "s/SKILL_NAME/$NAME/g" "$DIR/SKILL.md"

echo "Created: $DIR/"
echo "  $DIR/SKILL.md (template — edit to customize)"
echo "  $DIR/prompts/.gitkeep"
echo ""
echo "Next steps:"
echo "  1. Edit $DIR/SKILL.md with your skill's workflows"
echo "  2. Add prompt files to $DIR/prompts/"
echo "  3. Register the command in CLAUDE.md"
echo "  4. Open a PR"
