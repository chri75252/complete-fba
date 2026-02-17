# Test Plan: Verify Atlas/Sisyphus Workflow

**Created**: 2026-02-10
**Purpose**: Test that /start-work correctly invokes Atlas/Sisyphus execution agent

---

## Task 1: Create test file

### What to do
- Create file: `OUTPUTS/TEST_ATLAS_WORKFLOW/test.txt`
- Content: "Atlas workflow test - [timestamp]"
- Use current ISO timestamp

### Recommended Agent Profile
- **Category**: quick
  - Reason: Simple file creation task
- **Skills**: None required

### Parallelization
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1
- **Blocked By**: None

### Acceptance Criteria
- [ ] File exists: `OUTPUTS/TEST_ATLAS_WORKFLOW/test.txt`
- [ ] Content contains "Atlas workflow test"
- [ ] Command: `type OUTPUTS\TEST_ATLAS_WORKFLOW\test.txt` (Windows) or `cat OUTPUTS/TEST_ATLAS_WORKFLOW/test.txt` → shows expected content

---

## Task 2: Verify file created

### What to do
- Read file content
- Confirm it matches expected format

### Recommended Agent Profile
- **Category**: quick
  - Reason: Simple read operation
- **Skills**: None required

### Parallelization
- **Can Run In Parallel**: NO
- **Parallel Group**: Sequential
- **Blocked By**: Task 1

### Acceptance Criteria
- [ ] File content verified
- [ ] Report: "Atlas workflow test completed successfully"

---

## Task 3: Cleanup test file

### What to do
- Delete: `OUTPUTS/TEST_ATLAS_WORKFLOW/test.txt`
- Delete parent directory if empty

### Recommended Agent Profile
- **Category**: quick
  - Reason: Simple cleanup task
- **Skills**: None required

### Parallelization
- **Can Run In Parallel**: NO
- **Parallel Group**: Sequential
- **Blocked By**: Task 2

### Acceptance Criteria
- [ ] File deleted
- [ ] Command: `dir OUTPUTS\TEST_ATLAS_WORKFLOW` (Windows) or `ls OUTPUTS/TEST_ATLAS_WORKFLOW` → shows directory empty or doesn't exist

---

## Success Criteria

- [ ] All 3 tasks complete
- [ ] Test file created and verified
- [ ] Test file cleaned up
- [ ] Atlas/Sisyphus workflow invoked via /start-work
