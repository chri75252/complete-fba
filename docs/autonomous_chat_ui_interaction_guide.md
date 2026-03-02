# Autonomous Chat UI Interaction Guide

## 1. The Autonomous Paradigm

The Chat UI now utilizes an **Autonomous ReAct (Reason + Act) loop**. 
Instead of requiring you to command it one step at a time (1 prompt = 1 action), the MiniMax M2.5 agent will take your high-level goal and work through it autonomously in the background. It will "think", choose tools, and execute read-only operations automatically.

**How to watch it work:**
When you send a prompt, you will see a spinner labeled *"Agent is working..."*. Below this, it will print out its thought process in real-time (e.g., `Step 1: read_repo_file ✓`, `Step 2: query_financial ✓`).

**The Safety Gate (Approve & Execute):**
If the agent decides it needs to make a system change (like editing a file or queuing a massive scrape job), it will automatically pause the loop. An "Approve & Execute" button will appear on the screen. Once you click it, the agent performs the action and resumes its autonomous loop.

---

## 2. Launch Instructions

Because the LLM provider (`opencode`) is already securely configured via your `.env` system environment, you do not need to set redundant API keys. You simply need two terminals.

**Terminal 1: Start the Background Worker**
This executes the queued jobs (like the onboarding wizard or FBA runs).
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane worker
```

**Terminal 2: Start the Dashboard**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python dashboard\run_dashboard.py
```
*Wait for the dashboard to initialize and open `http://localhost:8501`.*

---

## 3. Powerful Multi-Step Prompts

Because the agent is autonomous, you can now give it massive, chained directives in a single sentence.

### A. Fetching Financial Data & Writing a Report
**Description:** Forces the LLM to query a CSV, interpret the data, and write a markdown file without stopping.
**Prompt:**
> *"Query the financial CSV for efghousewares.co.uk to find products with a positive ROI. Once you have the data, generate a detailed Markdown report summarizing the findings and save it to the control plane reports folder."*
**Expected Outcome:** The loop will run `query_financial`, parse the results, pause to ask you to approve the `write_output_file`, and then finish.

### B. Executing the Entire Supplier Onboarding Skill
**Description:** The ultimate test of autonomy. The LLM will read the skill, read your data, generate the JSON, and trigger the wizard.
**Pre-requisite:** You have dropped your raw categories/selectors text file into `setup/`.
**Prompt:**
> *"Execute the supplier onboarding skill for stationerywholesale.co.uk. The setup files are in setup/stationery_test.txt. No login required."*
**Expected Outcome:** The UI will show Step 1 (reading SKILL.md), Step 2 (reading your txt), and then pause for you to approve `write_output_file`. Once approved, it will resume and ask you to approve `enqueue_onboarding`. 

### C. Advanced Log Debugging
**Description:** The LLM reads a worker log, identifies the crash, and tells you what happened.
**Prompt:**
> *"Read the latest worker log, find the exact Python traceback that caused the crash, and summarize the root cause for me."*

---

## 4. Standard Workflow Prompts

You can still execute standard system workflows.

### A. Triggering Category Analysis (Sandbox)
**Prompt:**
> *"Start a category analysis for clearance-king.co.uk on: https://www.clearance-king.co.uk/smoking-products/lighters-accessories.html. Set max products to 10."*
**Expected Outcome:** The UI will pause and ask you to Approve the `enqueue_run` command.

### B. Interruption & Resumption
**Cancel Prompt:**
> *"Cancel the run immediately."*
**Resume Prompt:**
> *"Resume the cancelled run so we can finish analyzing the remaining products."*
**Expected Outcome:** The LLM remembers the `last_run_id` and the `sandbox_suffix`. It passes the suffix natively, and the worker log will print `RESUMPTION POINT CONFIRMED: Starting from category index X at product Y`.

---

## 5. Expected UI Behavior

When interacting with this new architecture, this is the exact flow you will experience on `http://localhost:8501`:

1.  **You hit Send.**
2.  A spinner appears: **"Agent is working..."**
3.  The agent begins writing its steps to the screen: 
    *   `Step 1: read_repo_file ✓`
    *   `Step 2: find_cached_products ✓`
4.  If it hits a Write action, the spinner turns orange: **"Waiting for approval..."**
5.  A big **"Confirm Execute"** button appears. You click it.
6.  The UI refreshes. The action executes. The spinner goes back to **"Agent is working..."**
7.  When the agent has achieved the final goal, it uses the `final_answer` tool. The spinner says **"Done"**, and the LLM's final markdown response prints beautifully into your chat history.