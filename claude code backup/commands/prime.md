---
allowed-tools: Bash, Read
description: Load context for a new agent session by analyzing codebase structure and README
---

# Prime

This command loads essential context for a new agent session by examining the codebase structure and reading the project README.

## Instructions
- Run the git command below to understand the codebase structure and file organization
- Read the README.md and CLAUDE.md files to understand the project purpose, setup instructions, and key information
- Provide a concise overview of the project based on the gathered context

## Context Analysis Command

```bash
#!/usr/bin/env bash

echo "=== All tracked files excluding unwanted patterns ==="
git ls-files -- \
  ':(exclude)*.log' \
  ':(exclude)*.csv' \
  ':(exclude)OUTPUTS/FBA_ANALYSIS/amazon_cache/**' \
  ':(exclude)archive_new/**' \
  ':(exclude)archive/**' \
  ':(exclude)testing/**' \
  ':(exclude)improvements/**' \
  ':(exclude)backup/**' \
  ':(exclude)OUTPUTS/FBA_ANALYSIS/amazon_cache_BACKUP_20250725_022306/**' \
  ':(exclude)OUTPUTS/FBA_ANALYSIS/amazon_cache - Copy/**' \
  ':(exclude)suppliers/**' \
  ':(exclude)tests/**' \
  ':(exclude)single use/**'

echo
echo "=== Latest 5 .log files (by commit date) ==="
git log --name-only --pretty=format: -- '*.log' \
  | grep '\.log$' \
  | awk '!seen[$0]++' \
  | head -n 5

echo
echo "=== Latest 5 .csv files (by commit date) ==="
git log --name-only --pretty=format: -- '*.csv' \
  | grep '\.csv$' \
  | awk '!seen[$0]++' \
  | head -n 5

echo
echo "=== Latest 5 files in amazon_cache (by commit date) ==="
git log --name-only --pretty=format: -- 'OUTPUTS/FBA_ANALYSIS/amazon_cache/**' \
  | grep 'OUTPUTS/FBA_ANALYSIS/amazon_cache/' \
  | awk '!seen[$0]++' \
  | head -n 5
```

## Required Reading
1. **README.md** - Project overview, setup instructions, key features
2. **CLAUDE.md** - Development standards, workflow guidelines, critical directives

## Output Format
Provide a concise summary including:
- Project name and primary purpose
- Key technologies and frameworks used
- Main workflow components
- Critical files and directories
- Current project state and priorities