# 🧠 GitNexus: Project Knowledge Graph Guide

GitNexus has been successfully installed and configured for the **Amazon FBA Agent System**. It has created a local knowledge graph of your entire codebase, mapping how every function, class, and variable interacts across your Python and JavaScript files.

## 🚀 How to Launch the Tool

To view your project's knowledge graph visually:

1.  **Open a Terminal** in the project root.
2.  **Run the Server**:
    ```bash
    npx gitnexus serve --port 3333
    ```
3.  **Open your Browser**: Go to [http://127.0.0.1:3333](http://127.0.0.1:3333)

You will see a 3D interactive map. You can click on nodes (files/functions) to see their dependencies and "blast radius."

---

## 🛡️ Excluded Files

To keep the "brain" focused on your actual logic and prevent it from getting bogged down by data or logs, I have excluded the following:

- **Heavy Directories**: `node_modules/**`, `venv/**`, `.git/**`
- **System Outputs**: `OUTPUTS/**` (Prevents indexing millions of scraped product JSONs)
- **Logs**: `logs/**`, `**/*.log`
- **Data Files**: `**/*.xlsx`, `**/*.csv`, `**/*.json` (excluding config)
- **Media**: `**/*.png`, `**/*.jpg`
- **Foreign Languages**: `**/*.kt`, `**/*.kts` (Kotlin), `**/*.java` (Java) - *These were causing native-build crashes on Windows.*

---

## ⚙️ How to Adjust Exclusions

If you want to include or exclude more files (for example, if you add a new data folder):

1.  Open the file: `.gitnexus/config.json`
2.  Modify the `"ignore"` array.
3.  **Re-index** the project to apply changes:
    ```bash
    npx gitnexus analyze .
    ```

---

## 💡 Real-Life Use Cases (Amazon FBA Project)

Here is how GitNexus specifically benefits your current workflow:

### 1. "Blast Radius" Analysis (Before Refactoring)
**Scenario**: You want to change how `FixedEnhancedStateManager.py` handles the `persistent_category_index`.
**GitNexus Use**: Search for the function in the UI. It will show you every single runner (`run_custom_*.py`) and utility that calls this index. You’ll know exactly which scripts you need to test before shipping the change.

### 2. Hunting Down "Ghost" Logic
**Scenario**: You see a log message about a "Circuit Breaker" but aren't sure which utility is triggering it.
**GitNexus Use**: Query the graph for `CircuitBreaker`. It will instantly map the relationship between `browser_manager.py`, `browser_circuit_breaker.py`, and the main workflow, showing you the exact "handshake" between them.

### 3. Onboarding New Suppliers
**Scenario**: You are using the `supplier-onboarding` skill to add a new wholesaler.
**GitNexus Use**: Use the "Impact" tool in the UI to see how `configurable_supplier_scraper.py` connects to the new runner. It helps you verify if the new supplier's pagination logic follows the established patterns of your other 8+ suppliers.

### 4. AI-Powered Deep Context (For Me/Other Agents)
Because GitNexus provides an **MCP Server**, when you ask me "Why is the Amazon extractor timing out?", I don't just "guess." I query the GitNexus graph to see the execution flow from the runner -> workflow -> extractor -> browser manager. It gives me "Senior Engineer" level sight into your code.
