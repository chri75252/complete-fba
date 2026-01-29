"""Brand Detection Module.

This module handles intelligent brand extraction and validation:
1. Extracts first 1-2 words from supplier titles as brand candidates
2. Maintains a persistent list of validated brands (memory/global/known_brands.json)
3. Only sends NEW unchecked candidates to AI for validation (token-efficient)
4. Supports incremental analysis as Excel file grows

Workflow:
    1. extract_brand_candidates(df) → Get all first 1/2 word combinations from titles
    2. load_checked_candidates() → Load previously checked candidates
    3. filter_new_candidates() → Only keep unchecked ones
    4. validate_brands_with_ai() → Send new candidates to AI for classification
    5. save_results() → Update known_brands.json and checked_candidates.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from fba_agent.text import normalize_title

if TYPE_CHECKING:
    from fba_agent.providers import BaseProvider


# File paths (relative to memory directory)
KNOWN_BRANDS_FILE = "global/known_brands.json"
CHECKED_CANDIDATES_FILE = "global/brand_candidates_checked.json"


# JSON Schema for AI brand validation
BRAND_VALIDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "validated_brands": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "candidate": {"type": "string"},
                    "is_brand": {"type": "boolean"},
                    "brand_name": {"type": "string"},  # Canonical brand name if is_brand=True
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "reason": {"type": "string"},
                },
                "required": ["candidate", "is_brand", "brand_name", "confidence", "reason"],
            },
        }
    },
    "required": ["validated_brands"],
}


def extract_brand_candidates(df: pd.DataFrame, title_column: str = "SupplierTitle") -> set[str]:
    """
    Extract brand candidates (first 1-2 words) from all supplier titles.
    
    Args:
        df: DataFrame with product data
        title_column: Column name containing supplier titles
        
    Returns:
        Set of unique brand candidates (normalized, uppercase)
    """
    candidates = set()
    
    # Words that are definitely NOT brands (common title starters)
    NOT_BRANDS = {
        "THE", "A", "AN", "NEW", "GENUINE", "ORIGINAL", "OFFICIAL", "PREMIUM",
        "PRO", "PROFESSIONAL", "QUALITY", "SUPER", "ULTRA", "MEGA", "MINI",
        "LARGE", "SMALL", "MEDIUM", "XL", "XXL", "BIG", "LITTLE",
        "SET", "PACK", "BOX", "KIT", "PAIR", "BUNDLE",
        "RED", "BLUE", "GREEN", "BLACK", "WHITE", "PINK", "PURPLE", "YELLOW",
        "BROWN", "GREY", "GRAY", "SILVER", "GOLD", "ORANGE",
        "CHRISTMAS", "EASTER", "HALLOWEEN", "VALENTINES", "BIRTHDAY",
        "HAPPY", "LOVE", "LED", "USB", "WOODEN", "METAL", "PLASTIC", "GLASS",
        "BBQ", "DOOR", "PET", "CAR", "HOME", "GARDEN", "KITCHEN", "BATHROOM",
        "STAINLESS", "STEEL", "BAMBOO", "CERAMIC", "SILICONE",
        "FOR", "WITH", "AND", "OR", "TO", "FROM", "BY", "IN", "ON", "OF",
    }
    
    for _, row in df.iterrows():
        title = str(row.get(title_column, ""))
        if not title or title == "nan":
            continue
            
        # Normalize title
        normalized = normalize_title(title)
        tokens = [t for t in normalized.split() if t and len(t) >= 2]
        
        if not tokens:
            continue
        
        # Skip if first word is definitely not a brand
        if tokens[0] in NOT_BRANDS:
            continue
            
        # Extract first word as candidate
        first_word = tokens[0]
        candidates.add(first_word)
        
        # Extract first TWO words as candidate (for multi-word brands)
        if len(tokens) >= 2 and tokens[1] not in NOT_BRANDS:
            two_words = f"{tokens[0]} {tokens[1]}"
            candidates.add(two_words)
    
    return candidates


def load_known_brands(memory_dir: Path) -> dict[str, str]:
    """
    Load the known brands dictionary.
    
    Returns:
        Dict mapping brand variants to canonical brand name
        e.g., {"CHEF": "CHEF AID", "CHEF AID": "CHEF AID"}
    """
    brands_path = memory_dir / KNOWN_BRANDS_FILE
    if brands_path.exists():
        try:
            with open(brands_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def load_checked_candidates(memory_dir: Path) -> set[str]:
    """Load the set of candidates that have already been checked by AI."""
    checked_path = memory_dir / CHECKED_CANDIDATES_FILE
    if checked_path.exists():
        try:
            with open(checked_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("checked", []))
        except Exception:
            return set()
    return set()


def save_known_brands(memory_dir: Path, brands: dict[str, str]) -> None:
    """Save the known brands dictionary."""
    brands_path = memory_dir / KNOWN_BRANDS_FILE
    brands_path.parent.mkdir(parents=True, exist_ok=True)
    with open(brands_path, "w", encoding="utf-8") as f:
        json.dump(brands, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(brands)} known brand mappings to {brands_path}")


def save_checked_candidates(memory_dir: Path, checked: set[str]) -> None:
    """Save the set of checked candidates."""
    checked_path = memory_dir / CHECKED_CANDIDATES_FILE
    checked_path.parent.mkdir(parents=True, exist_ok=True)
    with open(checked_path, "w", encoding="utf-8") as f:
        json.dump({"checked": sorted(checked)}, f, indent=2, ensure_ascii=False)


def build_brand_validation_prompt(candidates: list[str]) -> tuple[str, str]:
    """
    Build the prompt for AI brand validation.
    
    Args:
        candidates: List of brand candidates to validate
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = """You are a product brand identification specialist.

Your task is to analyze candidate words/phrases extracted from product titles and determine if each is a REAL BRAND NAME.

BRAND NAME criteria:
- A brand is a company name, manufacturer name, or product line name
- Examples of REAL brands: "CHEF AID", "MINKY", "PANASONIC", "BETTINA", "TONKITA", "DEKTON", "PYREX"
- Examples of NOT brands: "PREMIUM", "QUALITY", "STAINLESS STEEL", "CHRISTMAS", "GIANT"

For each candidate:
1. Determine if it's a real brand (is_brand: true/false)
2. If it IS a brand, provide the canonical brand name (might be longer than candidate)
3. Provide confidence (high/medium/low)
4. Brief reason for your decision

Respond ONLY with valid JSON."""

    candidates_text = "\n".join(f"- {c}" for c in candidates)
    
    user = f"""Analyze these {len(candidates)} candidate brand names extracted from product titles:

{candidates_text}

For EACH candidate, determine if it's a real brand name.

Return JSON with format:
{{
  "validated_brands": [
    {{
      "candidate": "CHEF AID",
      "is_brand": true,
      "brand_name": "CHEF AID",
      "confidence": "high",
      "reason": "Known UK kitchen accessories brand"
    }},
    {{
      "candidate": "PREMIUM",
      "is_brand": false,
      "brand_name": "",
      "confidence": "high",
      "reason": "Generic quality descriptor, not a brand"
    }}
  ]
}}"""

    return system, user


def validate_brands_with_ai(
    candidates: list[str],
    provider: "BaseProvider",
    batch_size: int = 50,
    max_batches: int = 10,  # Limit API calls per run to save tokens
) -> tuple[list[dict], list[str]]:
    """
    Send brand candidates to AI for validation.
    
    Args:
        candidates: List of candidate strings to validate
        provider: LLM provider instance
        batch_size: Maximum candidates per API call
        max_batches: Maximum number of API calls per run (to save tokens)
        
    Returns:
        Tuple of (validation_results, processed_candidates)
    """
    all_results = []
    processed_candidates = []
    
    total_batches = min(max_batches, (len(candidates) + batch_size - 1) // batch_size)
    
    # Process in batches up to max_batches
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(candidates))
        batch = candidates[start_idx:end_idx]
        
        system, user = build_brand_validation_prompt(batch)
        
        try:
            print(f"▶ Validating brands batch {batch_num + 1}/{total_batches} ({len(batch)} candidates)...")
            response = provider.chat_json(system, user, schema=BRAND_VALIDATION_SCHEMA)
            
            results = response.get("validated_brands", [])
            all_results.extend(results)
            processed_candidates.extend(batch)
            print(f"✓ Validated {len(results)} brand candidates")
            
        except Exception as e:
            print(f"⚠ Brand validation batch failed: {e}")
            # On failure, don't add to processed so they'll be retried
            continue
    
    remaining = len(candidates) - len(processed_candidates)
    if remaining > 0:
        print(f"[INFO] {remaining} candidates remain unvalidated (will be processed in future runs)")
    
    return all_results, processed_candidates


def run_brand_detection(
    df: pd.DataFrame,
    memory_dir: Path,
    provider: "BaseProvider | None" = None,
    title_column: str = "SupplierTitle",
    max_batches: int = 10,  # Limit to 10 batches (500 candidates) per run to save tokens
) -> dict[str, str]:
    """
    Run the complete brand detection workflow.
    
    1. Extract brand candidates from titles
    2. Load previously checked candidates
    3. Filter to only NEW unchecked candidates
    4. Validate new candidates with AI (if provider available, limited to max_batches)
    5. Update known brands and checked candidates
    
    Args:
        df: DataFrame with product data
        memory_dir: Path to memory directory
        provider: Optional LLM provider for AI validation
        title_column: Column containing supplier titles
        max_batches: Maximum number of API calls per run (to save tokens)
        
    Returns:
        Updated known brands dictionary
    """
    print("=" * 60)
    print("BRAND DETECTION STEP")
    print("=" * 60)
    
    # Step 1: Extract candidates from current data
    candidates = extract_brand_candidates(df, title_column)
    print(f"[EXTRACT] Found {len(candidates)} unique brand candidates from {len(df)} rows")
    
    # Step 2: Load existing data
    known_brands = load_known_brands(memory_dir)
    checked_candidates = load_checked_candidates(memory_dir)
    print(f"[MEMORY] Loaded {len(known_brands)} known brands, {len(checked_candidates)} previously checked candidates")
    
    # Step 3: Filter to only NEW unchecked candidates
    new_candidates = candidates - checked_candidates
    print(f"[NEW] Found {len(new_candidates)} NEW candidates to validate")
    
    if not new_candidates:
        print("✓ No new brand candidates to validate - using existing brand list")
        return known_brands
    
    # Step 4: Validate with AI (if provider available)
    if provider is None:
        print("⚠ No AI provider available - skipping brand validation")
        # Still mark as checked to avoid re-processing
        checked_candidates.update(new_candidates)
        save_checked_candidates(memory_dir, checked_candidates)
        return known_brands
    
    validation_results, processed = validate_brands_with_ai(
        candidates=sorted(new_candidates),
        provider=provider,
        batch_size=50,
        max_batches=max_batches,
    )
    
    # Mark processed candidates as checked
    checked_candidates.update(processed)
    
    # Step 5: Update known brands with validated results
    new_brands_count = 0
    for result in validation_results:
        candidate = result.get("candidate", "")
        is_brand = result.get("is_brand", False)
        brand_name = result.get("brand_name", "")
        
        # Mark as checked regardless of result
        checked_candidates.add(candidate)
        
        if is_brand and brand_name:
            # Add to known brands
            # Map the candidate to canonical brand name
            known_brands[candidate] = brand_name.upper()
            
            # Also add canonical name mapping to itself
            if brand_name.upper() not in known_brands:
                known_brands[brand_name.upper()] = brand_name.upper()
            
            new_brands_count += 1
    
    # Step 6: Save updated data
    save_known_brands(memory_dir, known_brands)
    save_checked_candidates(memory_dir, checked_candidates)
    
    print(f"✓ Added {new_brands_count} new brands to known brands list")
    print(f"✓ Total known brands: {len(known_brands)}")
    print("=" * 60)
    
    return known_brands


def get_brand_for_title(
    title: str,
    known_brands: dict[str, str],
) -> str | None:
    """
    Get the brand name for a title using the known brands dictionary.
    
    This replaces the simple first-word extraction with intelligent lookup.
    
    Args:
        title: Product title
        known_brands: Dictionary mapping variants to canonical brand names
        
    Returns:
        Canonical brand name if found, None otherwise
    """
    normalized = normalize_title(title)
    tokens = [t for t in normalized.split() if t and len(t) >= 2]
    
    if not tokens:
        return None
    
    # Check first TWO words as multi-word brand
    if len(tokens) >= 2:
        two_words = f"{tokens[0]} {tokens[1]}"
        if two_words in known_brands:
            return known_brands[two_words]
    
    # Check first word as brand
    if tokens[0] in known_brands:
        return known_brands[tokens[0]]
    
    return None
