#!/usr/bin/env python3
from pathlib import Path
import json
import re
import random
from typing import Any, List, Dict

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

BASE_DIR = Path(".")
OUTPUT_DIR = BASE_DIR / "supervised_matcher_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EFG_FINANCIAL_PATH = BASE_DIR / "fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_RECONCILED_20260410_001500.csv"
POUND_FINANCIAL_PATH = BASE_DIR / "fba_financial_report_poundwholesale-co-uk_20260414_082856.csv"

# Optional existing weak outputs. If these do not exist locally, replace this
# section with a direct call to the local weak matcher.
EFG_WEAK_OUTPUT_PATH = BASE_DIR / "probabilistic_matcher_outputs" / "efg_financial__probabilistic_output.csv"
POUND_WEAK_OUTPUT_PATH = BASE_DIR / "probabilistic_matcher_outputs" / "pound_financial__probabilistic_output.csv"

REVIEWED_LABELS_PATH = BASE_DIR / "reviewed_match_labels.csv"

SUPERVISED_TIER2_THRESHOLD = 0.85
SUPERVISED_TIER3_THRESHOLD = 0.35
SUPERVISED_BINARY_THRESHOLD = 0.50

AUTO_POSITIVE_CAP = 800
AUTO_NEGATIVE_CAP = 800
RANDOM_SEED = 42

MANUAL_ROW_WEIGHT = 4.0
AUTO_ROW_WEIGHT = 1.0

# ---------------------------------------------------------------------
# TEXT / EAN / FEATURE UTILITIES
# ---------------------------------------------------------------------

STOP_WORDS = {
    "the", "a", "an", "and", "or", "for", "of", "in", "to", "with", "is", "by", "on", "at", "from",
    "pack", "set", "new", "free", "pcs", "pc", "each"
}

NON_ALNUM_PAT = re.compile(r"[^a-z0-9\s]")
SPACE_PAT = re.compile(r"\s+")
NUM_PAT = re.compile(r"\b\d+(?:\.\d+)?\s?(?:ml|l|cm|mm|m|w|v|inch|inches|oz|kg|g|ltr|mah|led)?\b")
PACK_PATTERNS = [
    re.compile(r"\bpack of\s+(\d+)\b"),
    re.compile(r"\bset of\s+(\d+)\b"),
    re.compile(r"\b(\d+)\s*pk\b"),
    re.compile(r"\b(\d+)\s*pack\b"),
    re.compile(r"\b(\d+)\s*pcs\b"),
]


def norm_text(value: Any) -> str:
    text = "" if value is None else str(value).lower().strip()
    text = NON_ALNUM_PAT.sub(" ", text)
    text = SPACE_PAT.sub(" ", text)
    return text.strip()


def tokenize(value: Any) -> List[str]:
    return [t for t in norm_text(value).split() if t and t not in STOP_WORDS]


def normalize_ean(raw: Any) -> str:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s.lower():
        try:
            s = str(int(float(s)))
        except Exception:
            pass
    s = re.sub(r"[^0-9]", "", s)
    return s if len(s) in (8, 12, 13, 14) else ""


def gtin_checksum_valid(ean: str) -> bool:
    if not ean or len(ean) not in (8, 12, 13, 14) or not ean.isdigit():
        return False
    digits = [int(d) for d in ean]
    check = digits[-1]
    payload = digits[:-1]
    total = 0
    for i, d in enumerate(reversed(payload)):
        total += d * (3 if i % 2 == 0 else 1)
    expected = (10 - (total % 10)) % 10
    return expected == check


def extract_brand(value: Any) -> str:
    toks = tokenize(value)
    return toks[0] if toks else ""


def extract_pack_count(value: Any):
    text = norm_text(value)
    for pattern in PACK_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return None
    if re.search(r"\bsingle\b|\beach\b", text):
        return 1
    return None


def extract_numbers_units(value: Any) -> set:
    text = norm_text(value)
    return set(NUM_PAT.findall(text))


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def overlap_coeff(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def safe_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0

# ---------------------------------------------------------------------
# SIMPLE LOGISTIC REGRESSION (NUMPY ONLY)
# ---------------------------------------------------------------------


def sigmoid(x):
    x = np.clip(x, -30, 30)
    return 1.0 / (1.0 + np.exp(-x))


class SimpleLogistic:
    def __init__(self, lr=0.06, epochs=2500, l2=1e-3):
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        if sample_weight is None:
            sample_weight = np.ones_like(y)
        sample_weight = np.asarray(sample_weight, dtype=float)

        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)
        self.std_[self.std_ == 0] = 1.0
        Xs = (X - self.mean_) / self.std_

        self.coef_ = np.zeros(Xs.shape[1], dtype=float)
        self.intercept_ = 0.0
        ws = sample_weight / max(sample_weight.sum(), 1.0)

        for _ in range(self.epochs):
            p = sigmoid(Xs @ self.coef_ + self.intercept_)
            err = (p - y) * ws
            self.coef_ -= self.lr * (Xs.T @ err + self.l2 * self.coef_)
            self.intercept_ -= self.lr * err.sum()

        return self

    def predict_proba(self, X):
        X = np.asarray(X, dtype=float)
        Xs = (X - self.mean_) / self.std_
        p = sigmoid(Xs @ self.coef_ + self.intercept_)
        return np.column_stack([1 - p, p])

# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------


def binary_metrics(y_true, y_pred) -> Dict[str, float]:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    accuracy = (tp + tn) / max(len(y_true), 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# ---------------------------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------------------------


def build_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    rows = []
    for row in df.itertuples(index=False):
        supplier_title = getattr(row, "SupplierTitle", "")
        amazon_title = getattr(row, "AmazonTitle", "")

        s_tokens = set(tokenize(supplier_title))
        a_tokens = set(tokenize(amazon_title))
        shared_tokens = len(s_tokens & a_tokens)
        union_tokens = len(s_tokens | a_tokens)

        s_brand = extract_brand(supplier_title)
        a_brand = extract_brand(amazon_title)

        s_ean = normalize_ean(getattr(row, "EAN", ""))
        a_ean = normalize_ean(getattr(row, "EAN_OnPage", ""))

        s_nums = extract_numbers_units(supplier_title)
        a_nums = extract_numbers_units(amazon_title)

        s_pack = extract_pack_count(supplier_title)
        a_pack = extract_pack_count(amazon_title)

        supplier_price = safe_float(getattr(row, "SupplierPrice_incVAT", 0))
        selling_price = safe_float(getattr(row, "SellingPrice_incVAT", 0))
        price_ratio = selling_price / supplier_price if supplier_price > 0 and selling_price > 0 else 0.0

        rows.append([
            shared_tokens / union_tokens if union_tokens else 0.0,
            shared_tokens / min(len(s_tokens), len(a_tokens)) if s_tokens and a_tokens else 0.0,
            float(shared_tokens),
            float(len(s_nums & a_nums)),
            float(bool(s_brand and a_brand and s_brand == a_brand)),
            float(bool(s_brand and a_brand and s_brand != a_brand)),
            float(bool(s_ean and a_ean and s_ean == a_ean)),
            float(bool(s_ean and not a_ean)),
            float(bool(s_ean and a_ean and s_ean != a_ean)),
            float(s_pack is not None and a_pack is not None and s_pack == a_pack),
            float(s_pack is not None and a_pack is not None and s_pack != a_pack),
            float(price_ratio),
        ])

    return np.asarray(rows, dtype=float)

# ---------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------

if not EFG_FINANCIAL_PATH.exists():
    raise FileNotFoundError(f"Missing EFG financial report: {EFG_FINANCIAL_PATH}")
if not POUND_FINANCIAL_PATH.exists():
    raise FileNotFoundError(f"Missing Pound financial report: {POUND_FINANCIAL_PATH}")
if not REVIEWED_LABELS_PATH.exists():
    raise FileNotFoundError(f"Missing reviewed labels file: {REVIEWED_LABELS_PATH}")

efg = pd.read_csv(EFG_FINANCIAL_PATH)
efg["source"] = "efg"

pound = pd.read_csv(POUND_FINANCIAL_PATH)
pound["source"] = "pound"

full = pd.concat([efg, pound], ignore_index=True)
pound_offset = len(efg)

# ---------------------------------------------------------------------
# LOAD OR GENERATE WEAK BASELINE
# ---------------------------------------------------------------------

if EFG_WEAK_OUTPUT_PATH.exists() and POUND_WEAK_OUTPUT_PATH.exists():
    efg_weak = pd.read_csv(EFG_WEAK_OUTPUT_PATH)
    pound_weak = pd.read_csv(POUND_WEAK_OUTPUT_PATH)
    weak = pd.concat([efg_weak, pound_weak], ignore_index=True)
else:
    raise FileNotFoundError(
        "Weak output files were not found. Generate them first or adapt this script to call the local weak matcher directly."
    )

required_weak_cols = {"tier", "posterior_match_probability", "ean_exact_match"}
missing_weak_cols = required_weak_cols - set(weak.columns)
if missing_weak_cols:
    raise ValueError(f"Weak output files are missing required columns: {sorted(missing_weak_cols)}")

# ---------------------------------------------------------------------
# LOAD REVIEWED LABELS
# ---------------------------------------------------------------------

labels = pd.read_csv(REVIEWED_LABELS_PATH)
required_label_cols = {"source", "local_idx", "label_binary", "split"}
missing_label_cols = required_label_cols - set(labels.columns)
if missing_label_cols:
    raise ValueError(f"Reviewed labels file is missing required columns: {sorted(missing_label_cols)}")

labels = labels.copy()
labels["source"] = labels["source"].astype(str).str.strip().str.lower()
labels["local_idx"] = labels["local_idx"].astype(int)
labels["label_binary"] = labels["label_binary"].astype(int)
labels["split"] = labels["split"].astype(str).str.strip().str.lower()

allowed_sources = {"efg", "pound"}
allowed_splits = {"train", "validation", "holdout"}
if not set(labels["source"]).issubset(allowed_sources):
    raise ValueError("Reviewed labels file contains invalid source values")
if not set(labels["split"]).issubset(allowed_splits):
    raise ValueError("Reviewed labels file contains invalid split values")


def global_idx(source: str, local_idx: int) -> int:
    return local_idx if source == "efg" else pound_offset + local_idx

labels["global_idx"] = [global_idx(src, idx) for src, idx in zip(labels["source"], labels["local_idx"])]

# ---------------------------------------------------------------------
# BUILD FEATURES
# ---------------------------------------------------------------------

X_all = build_feature_matrix(full)

# ---------------------------------------------------------------------
# PARTITIONS
# ---------------------------------------------------------------------

train_labels = labels[labels["split"] == "train"].copy()
validation_labels = labels[labels["split"] == "validation"].copy()
holdout_labels = labels[labels["split"] == "holdout"].copy()

reviewed_idx = set(labels["global_idx"].tolist())
all_idx = set(range(len(full)))
available_auto_idx = all_idx - reviewed_idx

auto_positive_idx = [i for i in available_auto_idx if bool(weak.loc[i, "ean_exact_match"])]
auto_negative_idx = [
    i for i in available_auto_idx
    if weak.loc[i, "tier"] == "TIER_4_REJECTED"
    and float(weak.loc[i, "posterior_match_probability"]) < 0.01
]

rng = random.Random(RANDOM_SEED)
auto_positive_idx = rng.sample(auto_positive_idx, min(AUTO_POSITIVE_CAP, len(auto_positive_idx)))
auto_negative_idx = rng.sample(auto_negative_idx, min(AUTO_NEGATIVE_CAP, len(auto_negative_idx)))

manual_train_map = dict(zip(train_labels["global_idx"], train_labels["label_binary"]))
train_idx = list(manual_train_map.keys()) + auto_positive_idx + auto_negative_idx

auto_positive_set = set(auto_positive_idx)
y_train = np.asarray([
    manual_train_map[idx] if idx in manual_train_map else (1 if idx in auto_positive_set else 0)
    for idx in train_idx
], dtype=float)

sample_weight = np.asarray([
    MANUAL_ROW_WEIGHT if idx in manual_train_map else AUTO_ROW_WEIGHT
    for idx in train_idx
], dtype=float)

X_train = X_all[train_idx]

# ---------------------------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------------------------

model = SimpleLogistic(lr=0.06, epochs=2500, l2=1e-3)
model.fit(X_train, y_train, sample_weight=sample_weight)

# ---------------------------------------------------------------------
# EVALUATION
# ---------------------------------------------------------------------


def evaluate_partition(partition_df: pd.DataFrame, partition_name: str):
    if partition_df.empty:
        return {"partition": partition_name, "weak_probabilistic": None, "supervised": None}

    idx = partition_df["global_idx"].to_numpy()
    y_true = partition_df["label_binary"].to_numpy().astype(int)

    weak_pred = (weak.loc[idx, "tier"] != "TIER_4_REJECTED").astype(int).to_numpy()
    supervised_prob = model.predict_proba(X_all[idx])[:, 1]
    supervised_pred = (supervised_prob >= SUPERVISED_BINARY_THRESHOLD).astype(int)

    return {
        "partition": partition_name,
        "weak_probabilistic": binary_metrics(y_true, weak_pred),
        "supervised": binary_metrics(y_true, supervised_pred),
    }

validation_results = evaluate_partition(validation_labels, "validation")
holdout_results = evaluate_partition(holdout_labels, "holdout")

# ---------------------------------------------------------------------
# FULL INFERENCE
# ---------------------------------------------------------------------

full_supervised_prob = model.predict_proba(X_all)[:, 1]


def tier_from_supervised(row, prob: float) -> str:
    supplier_ean = normalize_ean(row.get("EAN", ""))
    amazon_ean = normalize_ean(row.get("EAN_OnPage", ""))

    if supplier_ean and amazon_ean and supplier_ean == amazon_ean and gtin_checksum_valid(supplier_ean) and gtin_checksum_valid(amazon_ean):
        return "TIER_1_VERIFIED"
    if prob >= SUPERVISED_TIER2_THRESHOLD:
        return "TIER_2_LIKELY"
    if prob >= SUPERVISED_TIER3_THRESHOLD:
        return "TIER_3_NEEDS_REVIEW"
    return "TIER_4_REJECTED"

full_out = full.copy()
full_out["weak_tier"] = weak["tier"].values
full_out["weak_probability"] = weak["posterior_match_probability"].values
full_out["supervised_probability"] = full_supervised_prob
full_out["supervised_binary_match"] = (full_supervised_prob >= SUPERVISED_BINARY_THRESHOLD).astype(int)
full_out["supervised_tier"] = [
    tier_from_supervised(full.iloc[i].to_dict(), full_supervised_prob[i])
    for i in range(len(full))
]

efg_out = full_out.iloc[:len(efg)].copy()
pound_out = full_out.iloc[len(efg):].copy()

efg_output_path = OUTPUT_DIR / "efg_financial__supervised_output.csv"
pound_output_path = OUTPUT_DIR / "pound_financial__supervised_output.csv"
benchmark_output_path = OUTPUT_DIR / "manual_holdout_benchmark.csv"
summary_output_path = OUTPUT_DIR / "supervised_experiment_summary.json"

efg_out.to_csv(efg_output_path, index=False)
pound_out.to_csv(pound_output_path, index=False)

if not holdout_labels.empty:
    holdout_idx = holdout_labels["global_idx"].to_numpy()
    y_holdout = holdout_labels["label_binary"].to_numpy().astype(int)
    weak_holdout_pred = (weak.loc[holdout_idx, "tier"] != "TIER_4_REJECTED").astype(int).to_numpy()
    supervised_holdout_prob = model.predict_proba(X_all[holdout_idx])[:, 1]
    supervised_holdout_pred = (supervised_holdout_prob >= SUPERVISED_BINARY_THRESHOLD).astype(int)

    benchmark_df = holdout_labels.copy()
    benchmark_df["SupplierTitle"] = full.loc[holdout_idx, "SupplierTitle"].values
    benchmark_df["AmazonTitle"] = full.loc[holdout_idx, "AmazonTitle"].values
    benchmark_df["weak_tier"] = weak.loc[holdout_idx, "tier"].values
    benchmark_df["weak_probability"] = weak.loc[holdout_idx, "posterior_match_probability"].values
    benchmark_df["weak_pred_binary"] = weak_holdout_pred
    benchmark_df["supervised_probability"] = supervised_holdout_prob
    benchmark_df["supervised_pred_binary"] = supervised_holdout_pred
    benchmark_df["weak_correct"] = (weak_holdout_pred == y_holdout).astype(int)
    benchmark_df["supervised_correct"] = (supervised_holdout_pred == y_holdout).astype(int)
    benchmark_df.to_csv(benchmark_output_path, index=False)

summary = {
    "config": {
        "efg_financial_path": str(EFG_FINANCIAL_PATH),
        "pound_financial_path": str(POUND_FINANCIAL_PATH),
        "reviewed_labels_path": str(REVIEWED_LABELS_PATH),
        "efg_weak_output_path": str(EFG_WEAK_OUTPUT_PATH),
        "pound_weak_output_path": str(POUND_WEAK_OUTPUT_PATH),
        "supervised_binary_threshold": SUPERVISED_BINARY_THRESHOLD,
        "supervised_tier2_threshold": SUPERVISED_TIER2_THRESHOLD,
        "supervised_tier3_threshold": SUPERVISED_TIER3_THRESHOLD,
        "manual_row_weight": MANUAL_ROW_WEIGHT,
        "auto_row_weight": AUTO_ROW_WEIGHT,
        "auto_positive_cap": AUTO_POSITIVE_CAP,
        "auto_negative_cap": AUTO_NEGATIVE_CAP,
    },
    "reviewed_label_counts": {
        "train": int(len(train_labels)),
        "validation": int(len(validation_labels)),
        "holdout": int(len(holdout_labels)),
    },
    "auto_label_counts": {
        "auto_positive": int(len(auto_positive_idx)),
        "auto_negative": int(len(auto_negative_idx)),
    },
    "validation_results": validation_results,
    "holdout_results": holdout_results,
    "output_files": {
        "efg_supervised_output": str(efg_output_path),
        "pound_supervised_output": str(pound_output_path),
        "holdout_benchmark": str(benchmark_output_path),
        "summary_json": str(summary_output_path),
    },
}

summary_output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
