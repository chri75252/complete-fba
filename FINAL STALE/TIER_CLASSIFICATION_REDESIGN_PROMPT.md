# FBA TIER CLASSIFICATION SYSTEM — FUNDAMENTAL REDESIGN PROMPT

## ROLE & OBJECTIVE

You are a **Principal Data Scientist** specializing in record linkage, entity resolution, and computational similarity analysis. Your task is to conduct **extensive, open-ended research** across academic papers, industry studies, and conceptual frameworks from ANY domain that could inform a fundamentally new approach to classifying product match confidence.

**This is NOT a threshold-tuning exercise.** The current system and all prior attempts have failed because they rely on the same flawed paradigm: a hand-tuned, additive point-scoring system. You must research broadly and propose a **completely different computational approach**.

---

## 1. PROBLEM STATEMENT

### The Core Problem

A financial report CSV contains rows where each row pairs a supplier product with an Amazon listing. The system must classify each row into one of 4 confidence tiers:

- **TIER_1_VERIFIED**: Confirmed match (exact EAN match, no conflicts)
- **TIER_2_LIKELY**: Probable match (strong signals but not definitive)
- **TIER_3_NEEDS_REVIEW**: Possible match (some signals, needs human review)
- **TIER_4_REJECTED**: No plausible match (auto-discarded)

**The system is catastrophically failing at TIER_4**: it dumps hundreds of obviously valid matches into TIER_4 because its scoring logic is too punitive. Products with matching brands, matching product types, and plausible EAN relationships are being rejected.

### Concrete Examples of False TIER_4 Rejections

These are ALL classified as TIER_4 but are clearly valid matches:

| Supplier Title | Amazon Title | Supplier EAN | Amazon EAN | Why TIER_4 is Wrong |
|---|---|---|---|---|
| CROSBY BLACK INSTANT POLISH 100ML | Crosby Shoe Polish Black 100ml - Instant Shoe Polish Black - Water Resistant -Pack of 2 | 5055566999768 | 5060911766001 | Same brand, same product, EAN mismatch = pack-of-2 vs single |
| WHAM BEEHIVE ROUND POT FAWN 40CM | Wham Set 4 Beehive 40cm Round Plastic Pot Cement Grey | 5057604101737 | 5057604505825 | Same brand, same product, EAN mismatch = color variant |
| INFAPOWER LED RECHARGE LANTERN | InfaPower Large Rechargeable Lantern F059 24 LED with USB Charging Cable | 5060240210794 | 5060240212491 | Same brand, same product, EAN mismatch = variant |
| FIT EMULSION BLOCK BRUSH | Fit For The Job Block Brush 4 inch Large Capacity for Emulsion | 5019200122646 | (missing) | Same brand, same product, Amazon EAN missing |
| SISTEMA TO GO DRESSING POTS 35ML 4PK | Sistema Dressing Pots To Go Food Container Sauce Pots With Lids 35 Ml | 9414202214706 | (missing) | Same brand, same product, Amazon EAN missing |
| STATUS LUGGAGE SCALE 16.06 | STATUS Mechanical Luggage Scale with Tape Measure | 5022822185012 | (missing) | Same brand, same product, Amazon EAN missing |
| MASTERPLUG 2 GANG 5MTR LEAD | Masterplug Two Socket Double Extension Lead, 5 Metre Cable | 5015056379173 | (missing) | Same brand, same product, Amazon EAN missing |
| SUPER DREAMER FITTED SHEET DOUBLE WHITE | Super Dreamer King Size Fitted Sheet White Clear Bedding Sheet | 5051346796060 | 5051346796077 | Same brand, same product, EAN mismatch = size variant |
| EVEREADY BATTERIES 6V 4R25 EACH | Eveready 4R25 6v Carbon zinco Battery | 5010419043517 | (missing) | Same brand, same product, Amazon EAN missing |
| PYREX CLASSIC CASSEROLE 2.1LTR PM | Pyrex Essentials Glass round Casserole High resistance 1.6 L | 3426470261500 | (missing) | Same brand, same product, capacity difference, Amazon EAN missing |
| ROLSON COMBINATION DISC LOCK 70MM | Rolson 66607 70mm Disc Padlock | 5029594665087 | 5029594666077 | Same brand, same product, EAN mismatch |
| ROOTS & SHOOTS GARDEN DECORATION SCARECROW | Roots & Shoots SET 3 GARDEN BOY SCARECROW | 5025572191456 | 5025572191494 | Same brand, same product, EAN mismatch |
| MASTERPLUG 4 GANG 2M SURGE | Masterplug Four Socket Extension Lead, 2 Metre Cable, Surge Protection | 5015056575483 | (missing) | Same brand, same product, Amazon EAN missing |
| DISHMATIC REFILLS 3PC BLACK | Dishmatic Extra Heavy-Duty Refills, Perfect For Tough Stains, 3 Pack | 5013931012825 | (missing) | Same brand, same product, Amazon EAN missing |
| PRODEC PREMIER ANGLED CUTTING BRUSH 1 INCH | ProDec 1 inch Premier Trade Professional Synthetic Long Handle Cutting In Paint Brush | 5019200237784 | (missing) | Same brand, same product, Amazon EAN missing |
| TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Sticks Perfect for Buffets | 5012904061204 | (missing) | Same brand, same product, Amazon EAN missing |
| STATUS SINGLE USB PLUG | Status USB A Charging Power Adaptor, 2400 mAh, White, Pack of 1 | 5022822185180 | (missing) | Same brand, same product, Amazon EAN missing |

From PoundWholesale (different supplier, same problem):

| Supplier Title | Amazon Title | Supplier EAN | Amazon EAN | Why TIER_4 is Wrong |
|---|---|---|---|---|
| World Of Pets Squeaky Vinyl Stick Dog Toy 30cm | CHIWAWA 4PCS 2.4" Squeak Latex Puppy Toy Funny Animal Sets | 5052516115629 | (missing) | Same product type, Amazon EAN missing |
| Jaunty Assorted Colour Happy Birthday Balloons 25 Pack | Dusico Balloons Rainbow Set (100 Pack) 12 Inches | 5056683920390 | (missing) | Same product type, Amazon EAN missing |
| Pan Aroma Assorted Mini Gel Scented Air Freshener 3 Pack | Pan Aroma Mini Gel Air Freshener, 9 Pack, Assorted Scents | 5053249268996 | 5053249254371 | Same brand, same product, pack difference, EAN mismatch |
| Stretcherz Super Squishy Braineez Wave 2 Toy Assorted | Stretcherz Electro Squad 4 Pack Super Stretchy Sensory Toys | 5050837663119 | (missing) | Same brand, same product line, Amazon EAN missing |
| 151 Masonry Brush 13cm X 4cm | 13 X 4CM Masonry Wall Stone Brick Paint Brush (Pack of 2) | 5050375058668 | (missing) | Same product, Amazon EAN missing |
| DID Jumbo Balloons Assorted Colours 30 Pack | 36 inch Giant Balloons 9 PCS Assorted Colour Big Balloon | 5056338305763 | (missing) | Same product type, Amazon EAN missing |
| Maxim 6W=40W Round Cool White E27 Es LED Light Bulb | Maxim LED Bulbs [Pack of 10] Type: Round (Cool White) 6Watts | 5022822207172 | (missing) | Same brand, same product, Amazon EAN missing |
| Smart Choice Squeaky Plush Treat Dispensing Dog Toy Assorted | PYue Puzzle Toys for Large Dogs, Interactive Dog Toys | 5052516216470 | (missing) | Same product type, Amazon EAN missing |
| Giftmaker Santa & Reindeer Christmas Pudding Gift Bag Large | Pack of 6 Paper Christmas Glitter Gift Bags with Gift Tags Rudolph Santa | 5012213544047 | (missing) | Same brand, same product, Amazon EAN missing |
| Prima Multi-Function Chrome Shower Head | Lara Multi Spray Shower Head - Chrome | 5038673230474 | (missing) | Same product type, Amazon EAN missing |
| Giftmaker Kraft Trees Christmas Gift Bag Large | Pack of 6 Paper Christmas Glitter Gift Bags with Gift Tags Rudolph Santa | 5012128583414 | (missing) | Same brand, same product, Amazon EAN missing |
| Escenti Kids Tea Tree Lice Repellent Hair Bands 8 Pack | Escenti Kids Head Lice Prevention Bundle: Head Lice Shampoo, Tea Tree Conditioner | 5053249263465 | (missing) | Same brand, same product line, Amazon EAN missing |
| Creator Zone Make Your Own Narwhal Handbag 35pc+ | ESSALOO Pen Creator Studio, Make Your Own Pens & Pen Making Kit for Kids | 5056175962907 | (missing) | Same product type, Amazon EAN missing |
| Marksman Cotton Garden Gloves | Fayear 12 Pairs White Cotton Protective Work Gloves | 5038673630267 | (missing) | Same product type, Amazon EAN missing |
| Aqua Cellulose Facial Cleansing Sponge 2pc | GAINWELL 50-Count Compressed Cellulose Facial Sponges | 8008990007520 | (missing) | Same product type, Amazon EAN missing |

---

## 2. WHAT HAS ALREADY BEEN TRIED (DO NOT REPEAT THESE APPROACHES)

### Attempt 1: Original Script (Pre-Fix)
**File**: `backup/tier_classification_fix_20260328/fba_report_filter.py` (339 lines)

**Approach**: Additive point-scoring system with these weights:
- EAN exact match: +50
- EAN checksum fail: +25
- EAN mismatch: -20
- Strong title match (sim ≥ 0.6, shared ≥ 4): +30
- Moderate title match (sim ≥ 0.35, shared ≥ 3): +15
- Very weak title match (sim < 0.15, shared < 2): -30
- Brand match (first word): +5
- Brand mismatch: -5
- Extreme price ratio (>20x): -15
- Category mismatch: -25
- Tier boundaries: T2 ≥ 40, T3 ≥ 15 (and net_profit > 0 required for T3)

**Why it failed**: The additive model is fundamentally broken. An EAN mismatch (-20) combined with a moderate title match (+15) and brand match (+5) = 0. That's TIER_4. But these are clearly the same product — just different variants or pack sizes.

### Attempt 2: Current Script (Post-Fix with loose_mode)
**File**: `tools/fba_report_filter.py` (356 lines)

**Approach**: Same additive model but with a `loose_mode` flag that relaxes thresholds:
- EAN mismatch: -10 (was -20)
- Strong title: sim ≥ 0.50, shared ≥ 3, bonus +30 (was ≥ 0.6, ≥ 4, +35)
- Moderate title: sim ≥ 0.25, shared ≥ 2, bonus +15 (was ≥ 0.35, ≥ 3, +20)
- Tier boundaries: T2 ≥ 25, T3 ≥ 5 (was ≥ 40, ≥ 15)
- Brand match: +10 (was +5)

**Why it still fails**: Even with relaxed thresholds, the fundamental paradigm is wrong. The additive model cannot distinguish between:
- "Same product, different pack size" (EAN mismatch, same brand, similar title)
- "Completely unrelated product" (EAN mismatch, different brand, different title)

Both get similar scores because the model doesn't understand product semantics.

### Attempt 3: Manual Analysis Prompts (LLM-Based Heuristics)
**Approach**: LLM-based manual analysis with decision trees, brand gates, unique anchor requirements, pack detection rules.

**Why it didn't lead to the best results**: These prompts encode human heuristics but don't solve the underlying computational problem. They're essentially sophisticated rule engines that still miss edge cases and require extensive manual tuning.

### Key Insight: What NOT to Do

**DO NOT** propose:
- Adjusting thresholds/weights in the additive model
- Adding more rules to the existing decision tree
- LLM-based manual analysis prompts
- Simple string similarity improvements (SequenceMatcher, Levenshtein, Jaro-Winkler alone)
- More keyword-based category detection
- First-word brand extraction

These have all been tried. The paradigm itself is the problem.

---

## 3. CURRENT CODEBASE CONTEXT

### Primary File: `tools/fba_report_filter.py`

The `classify_row(row, loose_mode=False)` function is the core classification logic. It:
1. Normalizes EANs (strip whitespace, remove .0, handle scientific notation, validate length/checksum)
2. Computes title similarity using `difflib.SequenceMatcher`
3. Counts shared tokens (set intersection after stop-word removal)
4. Extracts brand as first word of title
5. Applies additive scoring with configurable thresholds
6. Assigns tier based on confidence score

### Dashboard Integration: `dashboard_v2_redesign/api.py`

Endpoint `GET /api/analysis/{supplier}` calls `classify_row()` for each row in the financial report CSV and returns tiered results to the dashboard UI.

### Data Flow

```
Financial Report CSV → classify_row() → tier assignment → Dashboard API → UI
```

---

## 4. REQUIRED INPUT FILES (ATTACHED)

You will receive these 4 CSV files as attachments:

1. **EFG Dashboard Export**: `fba_analysis_2026-04-15.csv` (EFG, 681 rows)
2. **EFG Financial Report**: `fba_analysis_2026-04-15.csv` (EFG, raw format)
3. **PoundWholesale Dashboard Export**: `fba_analysis_2026-04-15 (1).csv` (~7183 rows)
4. **PoundWholesale Financial Report**: `fba_financial_report_poundwholesale-co-uk_20260414_082856.csv`

### Expected CSV Columns

| Column | Description |
|--------|-------------|
| `SupplierTitle` | Product title from supplier |
| `AmazonTitle` | Product title from Amazon listing |
| `EAN` | Supplier product barcode |
| `EAN_OnPage` | Amazon listing barcode |
| `ASIN` | Amazon Standard Identification Number |
| `SupplierPrice_incVAT` | Supplier cost including VAT |
| `SellingPrice_incVAT` | Amazon selling price |
| `NetProfit` | Pre-calculated profit |
| `ROI` | Return on Investment percentage |
| `bought_in_past_month` | Estimated monthly sales |
| `tier` | Current tier assignment |
| `confidence_score` | Current confidence score |
| `flags` | Current flags |
| `reasons` | Current classification reasons |

---

## 5. RESEARCH REQUIREMENTS — OPEN-ENDED EXPLORATION

### 5.1 Research Domains to Explore

Conduct research across these domains. Cite sources with URLs. Look for papers, studies, industry reports, and conceptual frameworks:

**A. Record Linkage / Entity Resolution**
- Fellegi-Sunter model and its modern variants
- Probabilistic record linkage theory
- Machine learning approaches to entity resolution
- Active learning for record linkage
- Blocking and indexing strategies for large-scale linkage
- How do Google, Amazon, eBay match products across catalogs?

**B. Natural Language Processing for Product Matching**
- Product title embedding models (what works best?)
- Transformer-based approaches for product matching
- Contrastive learning for product similarity
- How do e-commerce platforms handle title normalization?
- Named entity recognition for product attributes (brand, size, color, pack)

**C. Barcode / GTIN Systems**
- How do GTIN/EAN systems handle multipacks, variants, bundles?
- What is the relationship between single-unit EANs and multipack EANs?
- GS1 standards for variant encoding
- How should EAN mismatches be interpreted probabilistically?

**D. Similarity Metrics Beyond String Matching**
- Cosine similarity on TF-IDF vectors
- Word embeddings (Word2Vec, GloVe, FastText) for product titles
- Sentence transformers (SBERT) for semantic similarity
- Jaccard similarity on token sets
- Hybrid approaches combining multiple metrics

**E. Classification & Scoring Paradigms**
- Probabilistic classification vs. rule-based scoring
- Bayesian approaches to match confidence
- Ensemble methods for product matching
- Multi-stage cascading classifiers
- Learning-to-rank approaches

**F. Concepts from Other Domains**
- Information retrieval (BM25, vector search)
- Fuzzy matching at scale
- Graph-based entity resolution
- Clustering approaches for deduplication
- Anomaly detection for outlier rejection
- Any other conceptual frameworks that could apply

### 5.2 What to Look For

For each research area, identify:
1. **The core concept/algorithm** — What is it? How does it work?
2. **Why it might apply** — How does it solve the specific problems we're seeing?
3. **Implementation complexity** — Can it be implemented in Python? What libraries?
4. **Execution time** — Would it work for ~7000 rows in under 5-10 minutes?
5. **Evidence of success** — Has it been used successfully in similar contexts?

### 5.3 Computational Approach Proposals

Propose **at least 3 fundamentally different approaches**. For each:

1. **Describe the algorithm** in detail — not just "use embeddings" but exactly how
2. **Explain why it would work better** than the additive point-scoring model
3. **Provide pseudocode or actual Python code**
4. **List required Python libraries** (prefer standard library + common packages)
5. **Estimate execution time** for ~7000 rows
6. **Identify potential failure modes** and how to handle them

Consider approaches such as:
- **Probabilistic record linkage** (Fellegi-Sunter with EM algorithm)
- **Multi-stage cascading pipeline** (fast pre-filter → detailed analysis → final classification)
- **Embedding-based semantic matching** (sentence transformers + cosine similarity)
- **Feature engineering + supervised classification** (if labeled data can be derived)
- **Graph-based matching** (build similarity graph, use community detection or path analysis)
- **Ensemble of diverse matchers** (combine EAN logic, semantic similarity, brand detection, price ratio)
- **Bayesian confidence scoring** (compute P(match | evidence) rather than additive points)
- **Contrastive learning** (train a model to distinguish matches from non-matches)

---

## 6. DELIVERABLES

### 6.1 Research Report

A comprehensive research report covering:
- Summary of findings from each research domain
- Analysis of why the current additive model fails (with specific examples from attached CSVs)
- Comparison of at least 3 alternative approaches
- Recommendation of the best approach with detailed justification

### 6.2 Implementation Plan

A detailed, phased implementation plan:
- **Phase 1**: Research validation (test concepts on sample data)
- **Phase 2**: Core algorithm implementation
- **Phase 3**: Integration with existing codebase
- **Phase 4**: Calibration and validation

For each phase: specific code changes, expected improvement, execution time, risk assessment.

### 6.3 Python Implementation

Complete, runnable Python code for the recommended solution:
- Reads the attached CSV files
- Applies the new classification logic
- Outputs tier assignments with confidence scores
- Includes detailed logging/reasoning for each decision
- Compatible with the existing `tools/fba_report_filter.py` interface (drop-in replacement for `classify_row()`)

### 6.4 Validation Results

Run the proposed solution on the attached CSVs and report:
- Tier distribution before vs after
- Specific rows that changed tier (with reasoning)
- False positive/negative analysis
- Recommendations for threshold calibration

---

## 7. CONSTRAINTS & REQUIREMENTS

### Hard Constraints
- **No web browsing during classification**: The classification system itself must work offline using only the CSV data
- **Execution time**: Complete analysis should take **no more than 5-10 minutes** for ~7000 rows
- **Python compatibility**: Must work with Python 3.12+ and standard/common libraries
- **Backward compatibility**: Should be a drop-in replacement for `classify_row()`

### Quality Requirements
- **Precision for TIER_1**: Exact EAN matches must remain TIER_1
- **Recall for TIER_2/TIER_3**: Better to include borderline items than miss valid matches
- **TIER_4 should be truly unrelated**: Only products with no plausible match signal
- **Explainability**: Every classification decision must be traceable to specific evidence

### Output Format
- Markdown report with tables
- Python code in fenced code blocks
- Clear section headers
- No filler content

---

## 8. ADDITIONAL FILES TO REFERENCE

When analyzing the codebase, also examine:

1. **`tools/fba_report_filter.py`** — Current classification logic (primary target)
2. **`backup/tier_classification_fix_20260328/fba_report_filter.py`** — Original pre-fix version
3. **`dashboard_v2_redesign/api.py`** (lines 536-699) — Dashboard API integration

---

## 9. SPECIFIC QUESTIONS TO ANSWER

1. **Why does the additive scoring model fail?** Analyze the scoring math for specific examples from the attached CSVs. Show exactly which combination of penalties causes valid matches to be rejected.

2. **What is the optimal computational approach?** Compare at least 3 fundamentally different approaches. Which one gives the best balance of accuracy, speed, and maintainability?

3. **How should EAN evidence be weighted?** When both EANs are present but different, what does this mean probabilistically? When Amazon EAN is missing, how should confidence be calculated?

4. **How can product semantics be captured computationally?** What NLP techniques can extract brand, product type, attributes, pack size, and variant information from titles?

5. **What is the best tier boundary strategy?** Should thresholds be universal or supplier-specific? Should they be learned from data or set heuristically?

---

## 10. STOP CONDITIONS

Stop after generating:
1. **Research Report** — Comprehensive analysis of the problem and solutions
2. **Implementation Plan** — Phased plan with specific code changes
3. **Python Code** — Complete, runnable implementation
4. **Validation Results** — Before/after comparison on attached CSVs
5. **Summary** — Concise recommendations for next steps

---

## 11. STYLE REQUIREMENTS

- **Tone**: Direct, analytical, evidence-driven
- **Format**: Markdown with tables, code blocks, clear section headers
- **Evidence**: All claims backed by data from attached CSVs or cited research
- **No filler**: Every sentence must add value
- **Tables**: Fixed-width, aligned tables for data presentation

---

## 12. EXECUTION ORDER

1. **Read and analyze** all 4 attached CSV files
2. **Research** product matching methodologies across all domains listed above
3. **Analyze** the current and original `classify_row()` functions — identify ALL failure modes
4. **Propose** at least 3 fundamentally different computational approaches
5. **Recommend** the best approach with detailed justification
6. **Implement** the recommended solution in Python
7. **Validate** on attached CSVs and report results
8. **Generate** final recommendations

---

**BEGIN ANALYSIS NOW.**
