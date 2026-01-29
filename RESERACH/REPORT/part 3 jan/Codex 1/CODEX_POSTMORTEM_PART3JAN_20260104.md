# CODEX Post‑Mortem — Part 3 Jan (efghousewares) — 2026-01-04

**Scope:** Investigate why the first Part‑3 run stayed overly restrictive (and why the “updated prompts” didn’t prevent it), and sanity‑check whether the *current* listed entries in the Part‑3 CODEX report look internally consistent with the source spreadsheet.

## Files Verified (inputs + outputs)

- **Source XLSX:**  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\part 3 jan.xlsx` (2666 rows)
- **Preflight calibration output:**  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\Codex 1\CALIBRATION_PREFLIGHT_20260103.md`
- **CODEX generated report (current):**  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\Codex 1\PHASEA_MANUAL_REPORT_20260103.md`
- **Generator used to “execute” the prompts:**  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\Codex 1\generate_phasea_report_part3.py`

## What Went Wrong (Root Causes)

### 1) The main “guard” was not the prompts — it was the generator’s candidate gate

In the current generator, *most rows are silently skipped* unless they pass the `plausible` gate:

From `...\generate_phasea_report_part3.py:787`–`791`:

- `allow_without_brand = (not brand_match) and (overlap >= 6) and (sim >= 0.65)`
- `allow_high_sim = (not brand_match) and (sim >= 0.75) and (overlap >= 3)`
- `plausible = (brand_match and overlap >= 2 and sim >= 0.25) or allow_without_brand or allow_high_sim`
- `if not plausible: continue`

**Impact (measured from the XLSX using the same code paths):**

- Total rows in XLSX: **2666**
- Strict exact‑EAN rows: **41**
- Non‑exact rows: **2625**
- Non‑exact rows that pass `plausible`: **362**
- Non‑exact rows skipped entirely by `if not plausible: continue`: **2263**

So the report is effectively “Exact‑EAN rows + plausible non‑EAN rows”, not “full manual coverage”.

This is why “updated prompts” couldn’t fully fix the behavior: the execution path used a script that *hard‑coded* additional selection rules.

### 2) “Brand match” was implemented as “SupplierTitle prefix appears in AmazonTitle”

The generator’s brand detection is this (not a true brand field):

From `...\generate_phasea_report_part3.py:585`–`601`:

- `supplier_brand_tok = first_two_tokens(SupplierTitle)`
- `brand_in_amz = supplier_brand_tok in AmazonTitle OR first_token(SupplierTitle) in AmazonTitle`

Practical consequences:

- **False negatives (misses):** if the real brand is not at the start, or AmazonTitle omits it, the row is very likely to be **skipped** unless it meets the much stricter “no‑brand” thresholds.
- **False positives (wrong inclusions):** if the SupplierTitle starts with generic product words (e.g., `DOOR MAT`, `WATER DISPENSER`, `SALT PEPPER`), those can be treated as a “brand”, inflating matches that aren’t truly brand‑anchored.

This is also why your preflight calibration’s `brand_position = "start"` did not prevent the issue: it’s guidance, but the generator still uses a simplistic prefix‑matching heuristic.

### 3) The generator was forced to trade completeness for output size (implicit constraint)

Your quoted “initial run” behavior (e.g., *capping NEEDS VERIFICATION*) is not present in the **current** `generate_phasea_report_part3.py`, but it is consistent with the same underlying problem: the system tried to keep the markdown output manageable by:

- adding hard thresholds (similarity/overlap) and/or caps,
- and/or skipping large swathes of the data instead of producing a complete classification artifact.

Even without a “cap”, the current script still behaves like a cap because it “includes” only 403 rows and silently drops 2263.

### 4) Preflight correctly warned that the dataset is extremely noisy — but the generator still relies on weak signals

Preflight flagged the core data quality issue:

From `...\CALIBRATION_PREFLIGHT_20260103.md:47`:

> “SupplierTitle vs AmazonTitle had **very low token overlap in most rows**, suggesting many pairings may be mismatched; avoid using AmazonTitle-derived pack cues unless the pairing is validated.”

The data is indeed noisy. Example of rows skipped by the gate (these are not “missed opportunities”; they’re obvious mismatches despite high profit/sales):

- RowID 1: `151 WHITE NO-DRIP GLOSS PAINT 300ML` ↔ `LG OLED48C45LA ... Smart TV` (overlap=0)
- RowID 27: `AIRWICK CANDLE ...` ↔ `Lenovo ... Tablet` (overlap=0)
- RowID 53: `FAIRY WASHING UP LIQUID ...` ↔ `SIEMENS ... Coffee Machine` (overlap=0)

So **some restrictiveness is justified** for this supplier file: otherwise the report would be dominated by “TV/tablet” false positives.

However: the `plausible` thresholds still create *real misses* (next section).

## Evidence the Gate Caused Real Misses (Even When Rows Look Plausible)

Among the 2263 skipped non‑exact rows, there are at least **4** rows with *high similarity + decent overlap* that were skipped purely due to the thresholds:

- RowID 1486: `BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M` ↔ `3 x Easy Cut Refill Kitchen Foil ... 15m` (sim≈0.64, overlap=6)
- RowID 2607: `WHAM CRYSTAL 80LTR CLEAR BOX & LID` ↔ `CRYSTAL 80L BOX & LID CLEAR ...` (sim≈0.63, overlap=4)
- RowID 2298: `MARKSMAN KNIFE FOLDING LOCK BACK` ↔ `Rolson ... Folding Lock-Back Knife` (sim≈0.62, overlap=4)
- RowID 901: `ASHLEY SILICONE SLOTTED SPOON` ↔ `OXO ... Silicone Slotted Spoon` (sim≈0.61, overlap=3)

These rows would normally belong in **NEEDS VERIFICATION** (brand may be missing/mismatched, but the product type anchors are strong enough that verifying 1–2 details could upgrade).

## Are the *Current Listed Entries* Internally Consistent?

### 1) Report structure + counts

`...\PHASEA_MANUAL_REPORT_20260103.md` is internally consistent:

- Summary counts match the number of rows present in each table.
- Fixed‑width table formatting is intact (no pipe‑count corruption).

### 2) VERIFIED integrity

For the current report:

- All `VERIFIED` rows (33) correspond to **strict exact EAN** matches in the XLSX.
- The remaining strict exact‑EAN rows (41 total) appear as:
  - `FILTERED OUT` (7) due to Adjusted Profit <= 0 in the strict‑EAN path, and
  - `NEEDS VERIFICATION` (1) due to missing/zero Sales or price data in the strict‑EAN path.

This behavior is consistent with the generator logic at `...\generate_phasea_report_part3.py:732`–`784`.

### 3) Title “mismatches” found are explained by deliberate sanitation

Some Amazon titles differ between XLSX and report because the report sanitizes:

- `|` → `/` (preflight warned about this at `...\CALIBRATION_PREFLIGHT_20260103.md:41`)
- newlines → spaces

This is expected and not a data error.

## Why the “Updated Prompts” Didn’t Prevent This

Because execution was delegated to a generator script, the real “policy” became:

1) apply preflight‑derived parsing rules (dimension shield, spec‑x shield, table sanitization), **and**
2) apply a separate, script‑defined candidate gate (`plausible`) that is not specified (and can contradict) the manual prompt’s intent.

So the prompt improvements helped with:

- **pack parsing correctness** (dimension/spec shields),
- **table stability** (pipe sanitization),

but did **not** guarantee:

- “no missed products” coverage, because the script can still skip rows pre‑analysis.

## Surgical Fixes (Supplier‑Agnostic)

### Fix 1 — Replace silent dropping with explicit “excluded by gate” accounting

Keep the 4‑section report output **unchanged**, but add:

- a reconciliation line like: `Rows skipped by candidate gate: 2263`
- and write a companion file (CSV) listing `RowID` + reason (`not_plausible`) so nothing is silently lost.

This preserves readability while satisfying “no misses” auditability.

### Fix 2 — Stop treating SupplierTitle prefix as “brand”

Instead, generate a **brand lexicon** in preflight (supplier‑agnostic method):

- infer candidate brands as frequent leading tokens/phrases (e.g., top N first tokens) that are not measurement units and not generic nouns,
- then use that lexicon for brand matching.

This avoids both:

- missing real brands that aren’t the first 1–2 tokens, and
- promoting generic “DOOR MAT / WATER DISPENSER” prefixes as “brands”.

### Fix 3 — Relax the “no‑brand” path so plausible matches don’t get skipped

The current `allow_high_sim` requires `sim >= 0.75` **and** `overlap >= 3` (see `...\generate_phasea_report_part3.py:788`).

That combination demonstrably misses plausible rows (e.g., RowID 303 `PRIMA MULTI SHOWERHEAD CHROME` had sim≈0.76 but overlap=2).

Surgical change idea:

- allow `sim >= 0.75` with `overlap >= 2` (or a “model number match” rule) to route into **NEEDS VERIFICATION** rather than being skipped.

---

If you want, I can convert the above fixes into:

1) a patched `generate_phasea_report_part3.py` (with a backup created first), and  
2) a new “execution protocol” paragraph you can paste into the manual prompt so future runs can’t re‑introduce caps/silent drops.

