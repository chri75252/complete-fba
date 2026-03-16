# 🛠 Detailed Implementation Plan: Dashboard v2 Redesign

## 🎯 Context
The user has requested a comprehensive and surgical plan to integrate the modern UI/UX principles derived from the Stitch generated outputs into the existing dashboard framework, which has been cleanly isolated in the `dashboard_v2` directory.

We will accomplish this through:
1.  **Auto-Refresh Scope:** Implementing the new 3s and 5s refresh values.
2.  **Stitch Design Tokens:** Merging the custom CSS theme from Stitch screens.
3.  **UI/UX Pro Max Guidelines:** Applying rules such as "No-Line", "Glass & Gradient", removing pure white `#FFFFFF`, implementing transition animations, and adopting a geometric typography hierarchy (Sora `display` vs Manrope `label`).

---

## 🏗 Planned Implementations

### 1. Auto Refresh Dropdown Expansion
**Target File**: `dashboard_v2/templates/index.html`

*   **Current State:** Options start at `Disabled` (value="0") then skip to `30 seconds` (value="30").
*   **Action:** Add `<option value="3">3 seconds</option>` and `<option value="5">5 seconds</option>`.

**Diff Snippet:**
```diff
 <select id="refreshInterval" class="glass-input">
     <option value="0">Disabled</option>
+    <option value="3">3 seconds</option>
+    <option value="5">5 seconds</option>
     <option value="30">30 seconds</option>
     <option value="60" selected>60 seconds</option>
```

### 2. Stitch Pattern & Tailwind Theme Integration
**Target File**: `dashboard_v2/templates/index.html` (Head Section)
*   **Current State:** Hard-coded `style.css` without a centralized tokenized Tailwind config.
*   **Action:**
    1. Inject the Tailwind setup with the semantic variables from Stitch.
    2. Import the `Material Symbols Outlined` icons.
    3. Update the `body` styling class to embrace `bg-surface text-on-surface font-body`.

**Implementation Snippet:**
```html
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script id="tailwind-config">
    tailwind.config = {
        darkMode: "class",
        theme: {
            extend: {
                colors: {
                    "surface-container-lowest": "#0e0e0f",
                    "surface-container-low": "#1c1b1c",
                    "surface-container": "#201f20",
                    "surface-container-high": "#2a2a2b",
                    "surface-container-highest": "#353436",
                    "surface": "#131314",
                    "surface-dim": "#131314",
                    "on-surface": "#e5e2e3",
                    "on-surface-variant": "#c7c4d7",
                    "primary": "#c0c1ff",
                    "primary-container": "#8083ff",
                    "on-primary": "#1000a9",
                    "on-primary-container": "#0d0096",
                    "secondary": "#4edea3",
                    "secondary-container": "#00a572",
                    "on-secondary": "#003824",
                    "on-secondary-container": "#00311f",
                    "outline": "#908fa0",
                    "outline-variant": "#464554",
                    "error": "#ffb4ab",
                    "on-error": "#690005"
                },
                fontFamily: {
                    "headline": ["Space Grotesk"],
                    "body": ["Manrope"],
                    "label": ["Manrope"]
                }
            }
        }
    }
</script>
```

### 3. Glassmorphism & UI Component Refinement
**Target File**: `dashboard_v2/static/css/styles.css` & `dashboard_v2/templates/index.html`

*   **Current State:** Generic dark mode implementation using flat divs (`.card`, `.metrics-grid`).
*   **Action:**
    1. Implement the *Glass & Gradient* rule for floating elements (e.g. `bg-surface-variant/60 backdrop-blur-[20px]`).
    2. Overhaul the `.card` rules in `styles.css` to rely on Tailwind elevation (`bg-surface-container-low`, `border-outline-variant/10`).
    3. Revamp the primary buttons `.btn-primary` with Stitch's 135-degree Indigo Gradient and asymmetric padding `py-2.5 px-4`.
    4. Remove all hard 1px solid lines for card structures except subtle `outline-variant/10` to adhere to the Kinetic Vault "No-Line" rule.

**CSS Snippet (`dashboard_v2/static/css/styles.css` additions):**
```css
/* Custom Scrollbar from pro-max */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #131314; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #353436; border-radius: 2px; }

/* Metallic Action Gradients */
.btn-primary {
    background: linear-gradient(135deg, #c0c1ff 0%, #8083ff 100%);
    color: #1000a9;
    font-family: 'Space Grotesk', sans-serif;
    transition: transform 150ms ease, box-shadow 150ms ease;
    cursor: pointer;
}
.btn-primary:hover {
    transform: scale(0.98);
}

.glass-panel {
    background: rgba(53, 52, 54, 0.6);
    backdrop-filter: blur(20px);
}
```

### 4. Layout Restructuring (HTML Blocks)
**Target File**: `dashboard_v2/templates/index.html`

*   **Action:**
    1. Rewrite `<aside class="sidebar">` dropping custom CSS rules in favor of direct Tailwind definitions (e.g. `w-64 bg-surface-container-lowest border-r border-outline-variant/10`).
    2. Rewrite `<header class="view-header">` to act as the global TopNavBar using `h-16 flex items-center justify-between px-8 bg-surface-container-lowest/50 backdrop-blur-md border-b`.
    3. Rewrite Metric Cards to use `bg-surface-container-low p-5 rounded-lg border-l-2 border-secondary/40`, utilizing `font-headline` for the numbers (`Sora`/`Space Grotesk`) and `font-label text-outline` for the subtitle descriptors.
    4. Apply `cursor-pointer transition-colors duration-200` to interactive elements.

**Before Layout Example:**
```html
<div class="card metric-card">
    <div class="metric-label">Total Extracted</div>
    <div class="metric-value" id="totalExtracted">--</div>
    <div class="metric-sub">Supplier products</div>
</div>
```

**After Layout Example:**
```html
<div class="bg-surface-container-low p-5 rounded-lg border-l-2 border-primary/40 transition-colors hover:bg-surface-container cursor-pointer">
    <p class="text-[10px] font-label uppercase text-outline mb-2">Total Extracted</p>
    <p class="font-headline text-2xl font-semibold text-on-surface" id="totalExtracted">--</p>
    <p class="text-[10px] text-primary mt-1">Supplier Products</p>
</div>
```

---

## 🛠 `ui-ux-pro-max` & `stitch` Principles Used
*   **Stitch Tokens:** Retrieved absolute visual parity by using the exported JSON metrics (projects/5953506975597869581).
*   **Typography:** The font pairing rule has been utilized (`ui-reasoning` logic: `Space Grotesk/Sora` for numbers/headings; `Manrope` for dense data grids).
*   **Checklist Pre-flight:**
    *   No emojis as UI icons (strictly `Material Symbols Outlined`).
    *   `cursor-pointer` globally defined.
    *   Transition speeds placed at 150-200ms `ease`.

## ✅ Validation Checks
After running the code replacements, the workflow will be:
1.  **Code Syntax Check:** Lint the HTML tags for unclosed `<div>`.
2.  **App Mount Check:** Verify UI logic resolving appropriately without regressions.
3.  **Visual Render:** Sanity check the web rendering (verifying backdrop filters and background tier stacking).
