import re
import difflib
from typing import Dict, Any, Tuple

class FBATierClassifier:
    """
    Hybrid Probabilistic Record Linkage classifier for FBA products.
    Designed as a drop-in replacement for the legacy additive scoring system.
    """
    def __init__(self, config: Dict[str, float] = None):
        self.config = config or {
            "title_similarity_threshold_tier1": 0.85,
            "title_similarity_threshold_tier2": 0.70,
            "pack_size_penalty_weight": 0.50,
            "missing_ean_penalty": 0.20
        }
        
    def _normalize_text(self, text: str) -> str:
        """Standardize text for comparison."""
        if not text or str(text).lower() == 'nan': 
            return ""
        text = str(text).lower()
        return re.sub(r'[^a-z0-9\s]', '', text).strip()

    def _extract_pack_size(self, text: str) -> int:
        """Extracts numerical pack sizes (e.g., 'pack of 6', '6x') from titles."""
        match = re.search(r'(?:pack of|x)\s*(\d+)|(\d+)\s*(?:pack|pk|x)', str(text).lower())
        if match:
            return int(match.group(1) or match.group(2))
        return 1 # Default to single unit

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculates structural similarity ratio between two normalized strings."""
        if not str1 or not str2: return 0.0
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    def classify_row(self, row: Dict[str, Any]) -> Tuple[int, str, float]:
        """
        Evaluates a single product row and returns the Tier classification.
        
        Returns:
            Tuple containing: (Tier_Integer, Reason_String, Confidence_Float)
        """
        supp_title = self._normalize_text(row.get('Supplier Title', ''))
        amz_title = self._normalize_text(row.get('Amazon Title', ''))
        supp_ean = str(row.get('Supplier EAN', '')).strip()
        amz_ean = str(row.get('Amazon EAN', '')).strip()
        
        # 1. Feature Extraction
        ean_match = (supp_ean == amz_ean) and bool(supp_ean) and supp_ean.lower() != 'nan'
        ean_missing = not bool(supp_ean) or not bool(amz_ean)
        
        supp_pack = self._extract_pack_size(supp_title)
        amz_pack = self._extract_pack_size(amz_title)
        pack_match = (supp_pack == amz_pack)

        title_sim = self._calculate_similarity(supp_title, amz_title)

        # 2. Probabilistic Scoring
        confidence = title_sim
        if ean_match:
            confidence += 0.30
        elif ean_missing:
            confidence -= self.config['missing_ean_penalty']
        
        if not pack_match:
            confidence -= self.config['pack_size_penalty_weight']

        # Bound confidence between 0 and 1
        confidence = max(0.0, min(1.0, confidence))

        # 3. Decision Matrix
        if ean_match and pack_match and confidence >= self.config['title_similarity_threshold_tier1']:
            return 1, "Exact EAN and Pack Size Match", round(confidence, 3)
            
        elif ean_match and not pack_match:
            return 3, "EAN Match but Pack Size Discrepancy Detected", round(confidence, 3)
            
        elif title_sim >= self.config['title_similarity_threshold_tier1'] and pack_match:
            return 2, "High Title and Pack Match (EAN Missing/Mismatched)", round(confidence, 3)
            
        elif title_sim >= self.config['title_similarity_threshold_tier2']:
            return 3, "Moderate Title Similarity. Manual Review Required", round(confidence, 3)
            
        else:
            return 4, "Low Confidence / Structural Mismatch", round(confidence, 3)
