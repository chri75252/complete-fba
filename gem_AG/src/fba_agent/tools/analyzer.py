import re
import math
from typing import Dict, Any, Optional, Tuple, List
from fuzzywuzzy import fuzz
from .loader import DataLoader

class RowAnalyzer:
    """
    The deterministic brain of the agent.
    Analyzes a single row against the configuration to produce a Decision.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimension_shields = [re.compile(k, re.I) for k in config.get("dimension_shield_keywords", [])]
        self.spec_shields = [re.compile(k, re.I) for k in config.get("spec_x_shield_keywords", [])]
        
        # Pre-compile common pack patterns
        self.regex_pack_of_n = re.compile(r'(?:pack|pk|set|bundle)\s*of\s*(\d+)', re.I)
        self.regex_n_pack = re.compile(r'(\d+)\s*(?:pack|pk|pcs|pce|set|bag|roll|bot|bottle|can)', re.I)
        self.regex_leading_multiplier = re.compile(r'^(\d+)\s*x', re.I)
        self.regex_multipack_brackets = re.compile(r'\(\s*(\d+)\s*x\s*(\d+)\s*\)', re.I) # (4 x 50)
        self.regex_n_x_capacity = re.compile(r'(\d+)\s*x\s*\d+(?:ml|l|g|kg|oz|cl|cm|mm)', re.I) # 4 x 500ml

    def analyze_row(self, row: Dict[str, Any], override: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point for row analysis.
        Returns a dictionary representing the Decision Record (Ledger Row).
        """
        # 1. Parsing & Extraction
        sup_ean = str(row.get("SupplierEAN", "")).strip()
        amz_ean = str(row.get("AmazonEAN", "")).strip()
        sup_title = str(row.get("SupplierTitle", ""))
        amz_title = str(row.get("AmazonTitle", ""))
        
        # EAN Logic
        valid_sup, norm_sup = self._validate_ean(sup_ean)
        valid_amz, norm_amz = self._validate_ean(amz_ean)
        strict_match = (valid_sup and valid_amz and norm_sup == norm_amz)
        
        # Pack Logic
        sup_qty = self._extract_qty(sup_title)
        amz_qty, is_multipack_context = self._extract_amz_qty(amz_title)
        
        # RSU Calculation (Required Supplier Units)
        # If Amazon sells 200 (4 x 50) and Supplier sells 50 -> RSU = 4
        # If Amazon sells 10 and Supplier sells 1 -> RSU = 10
        rsu = 1
        pack_verdict = "1:1"
        
        if amz_qty > sup_qty:
            if sup_qty > 0:
                raw_rsu = amz_qty / sup_qty
                # We usually expect integer chunks. 
                # If 10 / 1 = 10. If 200 / 50 = 4.
                # If 10 / 6 = 1.66 -> Mismatch/Messy.
                if raw_rsu.is_integer():
                    rsu = int(raw_rsu)
                    pack_verdict = f"Bundle {rsu}x"
                else:
                    pack_verdict = "Pack Mismatch"
                    # Default to 1 to be conservative on cost, but flag it ???
                    # Logic: If mismatch, we can't reliably calc profit.
                    # But if we assume RSU = ceil(ratio), we are safe (costs more).
                    rsu = math.ceil(raw_rsu)
            else:
                rsu = amz_qty # Assume supplier is 1
                pack_verdict = f"Bundle {rsu}x"
        
        elif amz_qty < sup_qty:
            # Split candidate. Supplier 10, Amazon 1.
            # RSU is conceptually 1/10 aka 0.1.
            # But cost is full supplier price.
            # We do NOT adjust profit positively by default (conservative).
            rsu = 1 # Treat as buying 1 full supplier pack to sell 1 amazon unit
            pack_verdict = "Split Candidate"

        # Profit Logic
        supplier_price = float(row.get("SupplierPrice", 0))
        net_profit = float(row.get("NetProfit", 0))
        selling_price = float(row.get("SellingPrice", 0))
        
        adjusted_profit = self._calculate_adjusted_profit(
            net_profit, supplier_price, selling_price, rsu
        )

        # Title Match Score (0-100)
        title_score = fuzz.token_set_ratio(sup_title.lower(), amz_title.lower())
        
        # Brand Match (Simple heuristic for now)
        # In Phase 2 full, we'd use NLTK or more complex tokenization
        # Here we just check first word intersection or contained
        brand_match = self._check_brand_match(sup_title, amz_title)

        # 2. Bucketing
        bucket, filter_reason = self._determine_bucket(
            strict_match, 
            adjusted_profit, 
            pack_verdict, 
            brand_match, 
            title_score,
            rsu,
            override
        )

        # 3. Confidence Scoring
        confidence = self._calculate_confidence(
            strict_match, bucket, title_score, brand_match, rsu, valid_sup
        )

        # 4. Construct Result
        return {
            "RowID": row.get("RowID"),
            "Verdict": bucket,
            "Confidence": confidence,
            "SupplierTitle": sup_title,
            "AmazonTitle": amz_title,
            "Supplier EAN": sup_ean,
            "Amazon EAN": amz_ean,
            "ASIN": row.get("ASIN"),
            "SupplierPrice": supplier_price,
            "SellingPrice": selling_price,
            "NetProfit": net_profit,
            "ROI": row.get("ROI", 0),
            "Sales": row.get("Sales", 0),
            "Pack Verdict": str(pack_verdict),
            "Adjusted Profit": round(adjusted_profit, 2),
            "Key Match Evidence": self._generate_evidence(strict_match, brand_match, rsu),
            "Filter Reason": filter_reason,
            "IsUnrelated": (bucket == "UNRELATED")
        }

    def _validate_ean(self, ean: str) -> Tuple[bool, str]:
        """
        Returns (is_valid, normalized_ean).
        Validates checksum and length.
        """
        if not ean or ean in ["-", "nan", "None"]:
            return False, ""
        
        # Remove any non-digits
        digits = re.sub(r'\D', '', ean)
        
        if len(digits) not in [8, 12, 13, 14]:
            # Attempt left padding if < 14
             if 0 < len(digits) < 14:
                 # Padding logic is complex; try padding to 13 (most common) then 14
                 # Simple MVP: Do not auto-pad blindly, require strict input?
                 # PRD says "attempt left-padding".
                 # Let's try padding to 13.
                 padded = digits.zfill(13)
                 if self._check_gtin_checksum(padded):
                     return True, padded
                 return False, digits
             return False, digits

        if not self._check_gtin_checksum(digits):
             return False, digits
             
        return True, digits

    def _check_gtin_checksum(self, gtin: str) -> bool:
        """Standard GTIN checksum calc."""
        if not gtin.isdigit(): return False
        
        digits = [int(d) for d in gtin]
        check_digit = digits[-1]
        core_digits = digits[:-1]
        
        total = 0
        # Iterate reverse
        for i, d in enumerate(reversed(core_digits)):
            # Odd index (0-based from right) = val*3, Even = val*1
            # But enumerate is 0,1,2... 
            # GTIN-13: d12(chk), d11(x3), d10(x1)...
            weight = 3 if i % 2 == 0 else 1
            total += d * weight
            
        nearest_10 = math.ceil(total / 10) * 10
        calc_check = nearest_10 - total
        
        return calc_check == check_digit

    def _extract_qty(self, text: str) -> int:
        """Extracts simple quantity from Supplier or Amazon title."""
        # 1. Check Shields
        if self._is_shielded(text):
            return 1
            
        # 2. explicit patterns
        m = self.regex_pack_of_n.search(text)
        if m: return int(m.group(1))
        
        m = self.regex_n_pack.search(text)
        if m: return int(m.group(1))
        
        # defaults
        return 1

    def _extract_amz_qty(self, text: str) -> Tuple[int, bool]:
        """
        Extracts Amazon quantity. Returns (TotalQty, IsMultipack).
        Handles (4 x 50) logic.
        """
        # 1. Multipack brackets (4 x 50)
        m = self.regex_multipack_brackets.search(text)
        if m:
            outer = int(m.group(1))
            inner = int(m.group(2))
            # Basic sanity: if inner > 10, it looks like a count. 
            # If inner < 5, might be dimensions? e.g. (2 x 4) cm?
            # Check for dimensions nearby
            if not self._is_shielded(text):
                return (outer * inner, True)

        # 2. N x Capacity -> [N, True]
        m = self.regex_n_x_capacity.search(text)
        if m:
            return (int(m.group(1)), True)

        # 3. Leading multiplier "10 x ..."
        # Only if strict check enabled in config
        if self.config.get("leading_multiplier_check", True):
             m = self.regex_leading_multiplier.search(text)
             # But careful of "9 x 9 inch"
             if m and not self._is_shielded(text):
                 return (int(m.group(1)), True)

        # 4. Fallback to standard
        q = self._extract_qty(text)
        return (q, False)

    def _is_shielded(self, text: str) -> bool:
        """Returns True if text contains dimension or spec keywords."""
        for p in self.dimension_shields:
            if p.search(text): return True
        for p in self.spec_shields:
            if p.search(text): return True
        return False

    def _calculate_adjusted_profit(self, 
        net_profit: float, 
        sup_price: float, 
        sell_price: float, 
        rsu: int
    ) -> float:
        """
        Adjusted Profit = NetProfit - (SupPrice * (RSU - 1))
        (Assuming NetProfit was based on buying 1 unit).
        
        If RSU = 1, adj = net_profit.
        If RSU = 4, we pay for 3 extra units.
        """
        if rsu < 1: rsu = 1
        return net_profit - (sup_price * (rsu - 1))

    def _check_brand_match(self, t1: str, t2: str) -> bool:
        # MVP: First word match
        try:
            b1 = t1.split()[0].lower()
            b2 = t2.split()[0].lower()
            return b1 == b2
        except:
            return False

    def _determine_bucket(
        self, 
        strict_match: bool, 
        adj_profit: float, 
        pack_verdict: str,
        brand_match: bool,
        title_score: int,
        rsu: int,
        override: Optional[Dict]
    ) -> Tuple[str, str]:
        
        if override:
            return override.get("bucket"), "Manual Override"

        reason = "-"

        # 1. Filtered Out / Unrelated checks
        if adj_profit <= 0:
            return "FILTERED_OUT", "Negative Adjusted Profit"
        
        if title_score < 20:
            return "UNRELATED", "Low Text Similarity"

        # 2. VERIFIED Logic
        if strict_match:
            # Check for Pack Mismatch
            if "Mismatch" in pack_verdict:
                return "FILTERED_OUT", "EAN Match but Pack Mismatch"
            if "Split" in pack_verdict:
                 return "NEEDS_VERIFICATION", "Split Candidate (EAN Match)"
            return "VERIFIED", reason
            
        # 3. Non-EAN Logic
        if brand_match:
            if title_score > 60 and rsu == 1:
                return "HIGHLY_LIKELY", "Strong Brand+Title Match"
            if title_score > 40:
                return "NEEDS_VERIFICATION", "Good Brand Match, Verify Pack/Variant"
        
        # 4. Fallback
        if title_score > 80:
             return "NEEDS_VERIFICATION", "High Title Sim, Brand Mismatch?"
             
        return "UNRELATED", "Insufficient Evidence"

    def _calculate_confidence(self, strict: bool, bucket: str, title: int, brand: bool, rsu: int, valid_sup: bool) -> int:
        score = 0
        if strict: 
            score = 95
        else:
            if brand: score += 35
            if title > 50: score += 25
            if rsu == 1: score += 10
            if valid_sup: score += 5
        
        # Penalties based on bucket
        if bucket == "NEEDS_VERIFICATION":
            score = min(score, 75)
        if bucket == "UNRELATED":
            score = min(score, 20)
            
        return max(0, min(100, score))

    def _generate_evidence(self, strict: bool, brand: bool, rsu: int) -> str:
        parts = []
        if strict: parts.append("Exact EAN Match")
        if brand: parts.append("Brand Match")
        if rsu > 1: parts.append(f"Multipack (x{rsu})")
        return ", ".join(parts)
