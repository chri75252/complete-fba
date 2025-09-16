"""
Product Data Validator for Amazon FBA Agent System
Validates extracted product data against expected formats and business rules.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

log = logging.getLogger(__name__)


class ProductValidator:
    """Validates product data for quality and completeness."""
    
    def __init__(self):
        """Initialize validator with validation rules."""
        self.required_fields = {
            'supplier': ['title', 'price', 'url'],
            'amazon': ['title', 'asin', 'current_price'],
            'combined': ['supplier_product_info', 'amazon_product_info']
        }
        
        self.price_limits = {
            'min': 0.01,
            'max': 100000.00
        }
        
        self.weight_limits = {
            'min_pounds': 0.01,
            'max_pounds': 150.0  # FBA limit
        }
        
        self.dimension_limits = {
            'min_inches': 0.1,
            'max_length_inches': 108.0,  # FBA oversize limit
            'max_girth_inches': 165.0  # Length + 2*(Width + Height)
        }
        
        # Restricted keywords for FBA
        self.restricted_keywords = [
            # Hazmat
            'battery', 'batteries', 'lithium', 'flammable', 'explosive',
            'chemical', 'hazardous', 'toxic', 'corrosive', 'radioactive',
            
            # Restricted categories
            'weapon', 'knife', 'gun', 'ammunition', 'tobacco', 'vape',
            'e-cigarette', 'alcohol', 'drug', 'pharmaceutical', 'prescription',
            
            # Adult content
            'adult', 'sex', 'erotic', 'pornographic',
            
            # Counterfeit risks
            'replica', 'fake', 'copy', 'knockoff', 'imitation'
        ]

    def validate_supplier_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate supplier product data.
        
        Args:
            product_data: Supplier product data dict
            
        Returns:
            Validation result with status and issues
        """
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'data_quality_score': 100.0
        }
        
        # Check required fields
        for field in self.required_fields['supplier']:
            if field not in product_data or not product_data[field]:
                validation_result['valid'] = False
                validation_result['issues'].append(f"Missing required field: {field}")
                validation_result['data_quality_score'] -= 20
        
        # Validate title
        title_validation = self._validate_text_field(product_data.get('title'), "Supplier Title", min_length=5, max_length=500, restricted_keywords_check=True)
        if not title_validation['valid']:
            validation_result['valid'] = False
            validation_result['issues'].extend(title_validation['issues'])
        validation_result['warnings'].extend(title_validation.get('warnings', []))
        
        # Validate price
        if 'price' in product_data:
            price_validation = self._validate_price(product_data['price'])
            if not price_validation['valid']:
                validation_result['valid'] = False
                validation_result['issues'].extend(price_validation['issues'])
            validation_result['warnings'].extend(price_validation.get('warnings', []))
        
        # Validate URL
        if 'url' in product_data:
            url_validation = self._validate_url(product_data['url'])
            if not url_validation['valid']:
                validation_result['valid'] = False
                validation_result['issues'].extend(url_validation['issues'])
        
        # Validate identifiers if present
        if product_data.get('ean'):
            ean_validation = self._validate_ean(product_data['ean'])
            if not ean_validation['valid']:
                validation_result['warnings'].append(f"Invalid Supplier EAN: {ean_validation['issue']}")
                validation_result['data_quality_score'] -= 5
        
        # Validate description
        desc_validation = self._validate_text_field(product_data.get('description'), "Supplier Description", min_length=10, max_length=3000, allow_empty=True, restricted_keywords_check=True)
        if not desc_validation['valid']: # Not a hard fail for description
            validation_result['warnings'].extend(desc_validation['issues'])
            validation_result['data_quality_score'] -= 5
        validation_result['warnings'].extend(desc_validation.get('warnings', []))

        # Validate images
        img_validation = self._validate_image_urls(product_data.get('images'), "Supplier Images")
        if not img_validation['valid']: # Not a hard fail for images
            validation_result['warnings'].extend(img_validation['issues'])
            validation_result['data_quality_score'] -= 5
        validation_result['warnings'].extend(img_validation.get('warnings', []))
        
        # Validate brand
        brand_validation = self._validate_text_field(product_data.get('brand'), "Supplier Brand", min_length=1, max_length=100, allow_empty=True)
        if not brand_validation['valid']:
             validation_result['warnings'].extend(brand_validation['issues']) # Not a hard fail
        validation_result['warnings'].extend(brand_validation.get('warnings', []))

        # Validate model number
        model_validation = self._validate_text_field(product_data.get('model_number'), "Supplier Model Number", min_length=1, max_length=50, allow_empty=True)
        if not model_validation['valid']:
             validation_result['warnings'].extend(model_validation['issues']) # Not a hard fail
        validation_result['warnings'].extend(model_validation.get('warnings', []))

        # Validate extracted weight and dimensions
        weight_val = self._validate_extracted_weight(product_data.get('weight'))
        if not weight_val['valid']:
            validation_result['issues'].extend([f"Supplier Weight: {issue}" for issue in weight_val['issues']])
        validation_result['warnings'].extend([f"Supplier Weight: {warn}" for warn in weight_val['warnings']])

        dim_val = self._validate_extracted_dimensions(product_data.get('dimensions'))
        if not dim_val['valid']:
            validation_result['issues'].extend([f"Supplier Dimensions: {issue}" for issue in dim_val['issues']])
        validation_result['warnings'].extend([f"Supplier Dimensions: {warn}" for warn in dim_val['warnings']])

        # Check for restricted products (based on title and description)
        # This uses the internal restricted_keywords list
        if self._is_text_restricted(product_data.get('title',"") + " " + product_data.get('description',"")):
            validation_result['valid'] = False
            validation_result['issues'].append(f"Restricted product based on title/description keywords.")
            validation_result['data_quality_score'] -= 30

        # Calculate final quality score
        validation_result['data_quality_score'] = max(0, validation_result['data_quality_score'])
        
        return validation_result

    def validate_amazon_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Amazon product data.
        
        Args:
            product_data: Amazon product data dict
            
        Returns:
            Validation result with status and issues
        """
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'data_quality_score': 100.0
        }
        
        # Check required fields
        for field in self.required_fields['amazon']:
            if field not in product_data or not product_data[field]:
                validation_result['valid'] = False
                validation_result['issues'].append(f"Missing requiŸ’˘ °c◊   (Ìö                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
$7 ÊUÆtéÊœÜ
§
-	∞	.≤E’ıÄ°+µA”d7                                                                                                                                                                                                                                                                                                                                                                                                                                        Å%e	o%Åolder version/good/utils/windows_save_guardian.pyprocess_nodesuccess7e81b1cf5b3bd76c4451ced5c2a86c1a7cecef2326021064869888795697456fb¢J˛/¡DeÉ”gçúeÉ’ªôÄÅ&d	q%Åolder version/good/utils/windows_memory_manager.pyprocess_nodesuccess177c9d97a6b6c0d6c0f21107a0655bd5cde6f439b21fd34f9bb4599a757143f9b¢Js¿º¸eÉ”eæ<òeÉ’π  òk -%Utest_roi_fix.pyprocess_nodeinitd640lÅL=%Utest_source_url_fixes.pyprocess_nodeinit329bd637-df39-48e2-ba9c-6555ae772d8fc5πªC‰eÉ”1W‰c5œ÷”ö0kÅK;%Utest_state_api_fixes.pyprocess_nodeinit311e7b03-3ee5-4bde-b3a8-36138528c73dc/ê¢ç˜ƒeÉ”˝¯úc0F∏Î(qÅJG%Utest_save_state_atomic_fix.pyprocess_nodeinit38993ac0-8d64-4ce6-a1a2-b657ef1fbf39c.N®»ﬂÑeÉ”ÒœËc.VIç7tsÅIK%Utest_surgical_implementation.pyprocess_nodeinit9f835f24-a486-46f8-8c1a-e87f12a76f3db·´Õ$’eÉ”	∂“b·¥ç:Ê,sÅHK%Uutils/atomic_file_operations.pyprocess_nodeinit04f92db4-cf80-45f4-b55f-61824960c5c7b≥Ÿ√o eÉ“Êı&$bπ·ÿí‰jÅG9%Uwsl_compatible_save.pyprocess_nodeinit08ea2029-f9cd-4a77-88fa-91f22587fbc3b¢Kw¨@eÉ”x˚Xb¢`Èw5(oÅFC%Uutils/wsl_memory_manager.pyprocess_nodeinitc86a6218-8e5e-4304-a8e3-8a5a55910194b¢K2´ÃeÉ“Ïü¸b¢`‰ƒvlrÅEI%Uutils/windows_save_guardian.pyprocess_nodeinit3b1e7057-66d7-4584-af49-b9262d750078b¢KÍ eÉ“ÏX>îc9Îõ˙!HsÅDK%Uutils/windows_memory_manager.pyprocess_nodeinitd23bb634-9224-4e67-8789-2b48daf3bc9fb¢K∞k®eÉ“Ï˚b¢`‘iö|- j3%Uutils/url_filter.pyprocess_nodeinitbfc5d5c8-0edf-4503-aba8-6ccc69b81fb6b¢K|LeÉ“Î“kòb¢`Œb–îmÅ??%Uutils/sentinel_monitor.pyprocess_nodeinit1fafe2c7-f4ee-4cb2-85e6-1755a33c742db¢KØveÉ“Í∂$ee†dﬂ÷ÑjÅ=9%Uutils/normalization.pyprocess_nodeinita4e74eff-8200-4c84-a9cb-c4edd38a16dcb¢KBŸ∏eÉ“Í*7ÄcÑ!°‰úyÅ:W%Uutils/fixed_enhanced_state_manager.pyprocess_nodeinit9bf98790-dbcf-4c13-b6ad-dd4bb1a646ffb¢K§€<eÉ“ÈV÷úe}]≥Cº0Åc%Utools/passive_extraction_workflow_latest.pyprocess_nodeinit4e2efb62-c3ae-4697-b5cd-24acbae7fee8b¢Kø(leÉ“¯›Âte}q!$îzÅY%Utools/configurable_supplier_scraper.pyprocess_nodeinit64024282-2b86-4002-b33f-5e0ce96fd0b3b¢Kƒ@eÉ“Ò©»cÑ:a5	‰u|O%Utools/FBA_Financial_calculator.pyprocess_nodeinit58ed0b7e-2564-4a15-9b0e-615b1bfb2b89b¢KÛ‚teÉ“Ó\8lep∫}$˜∏piE%Urun_custom_poundwholesale.pyprocess_nodeinitb8e72ff6-4399-44e4-833a-a8cfcb319fc9b¢J˛‡ÛƒeÉ”Ñ‡eq®Fú≤†kÅM;%Uci_source_url_guards.pyprocess_nodeinitc8f880de-1a92-4e4f-a264-cc6f019bc1b8c5’d’\eÉ”†úƒc5ﬁ-gˇ¸Å$g	s%Åolder version/passive_extraction_workflow_latest.pyprocess_nodeinit42120bbe59b1c8bf4eec45b42c60a7b6ac325a7c2351234975aec7205e73df7eb¢J˛ï‘eÉ“⁄ì†eÉ∏óµ[Ñ   ¢i%Åolder version/good/utils/wsl_memory_mohA%hÅC3%Uutils/url_filter.pyprocess_nodedoingbfc5d5c8-0edf-4503-aba8-6ccc69b81fb6b¢K|LeÉ‘by¯b¢`Œb–îÅ"f	i%Åolder version/good/utils/wsl_memory_manager.pyprocess_nodesuccessc8dc9b33b961c0cb6169aa4f2f967a83e184eb9662ea5a390e11418efcfb37c7b¢J˛a˝eÉ”i9)åeÉ’ΩEåÅc	Y%Åolder version/good/utils/url_filter.pyprocess_nodeinitcef14baa46c56f626e1830d7dd9936bf4e0ddb507c54d3ecf4cd49e758c23a22b¢Jsè§eÉ“≥ö,eÉº¸ÓêÅb	e%Åolder version/good/utils/url_cache_filter.pyprocess_nodeinit15b8c1147a12e9b6c032bdbac0c6f4b0465cd2633a0301c5acd8ba9876898472b¢Js]
∏eÉ“œ∫(eÉº˙—(Å$a	s%Åolder version/good/utils/url_aware_state_manager.pyprocess_nodeinitf6fea52903655d7ed1cdb97d0c4053c37173d7cdaa49da0159d5bfc81f2c1ee1b¢Js6MàeÉ“ŸteÉºˆ>◊®Å(`	u%Åolder version/good/utils/supplier_circuit_breaker.pyprocess_nodesuccessb41d80f2c6d4f3046780fc884ae36d8db7a96f291ed0732ba0de960ad011ebe1b¢Js”ËeÉ”d,oDeÉ’∏8SD(ÌË   SQLite format 3   @   "$*       ¡   -                                             "$* .r†   Ï ˚Ω
+	@¿n±7ΩC…n∏QÏ                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              c-Åindexidx_stageworkspace_recordCREATE UNIQUE INDEX idx_stage
    ON workspace_record (stage)e'#Åindexidx_file_pathfile_recordCREATE UNIQUE INDEX idx_file_path
    ON file_record (file_path)Y1{indexidx_edge_file_pathedgeCREATE INDEX idx_edge_file_path
    ON edge (file_path)Y1{indexidx_edge_target_idedgeCREATE INDEX idx_edge_target_id
    ON edge (target_id)Y1{indexidx_edge_source_idedgeCREATE INDEX idx_edge_source_id
    ON edge (source_id)xEÅ#indexidx_node_segmentation_field4nodeCREATE INDEX idx_node_segmentation_field4
    ON node (segmentation_field4)xEÅ#indexidx_node_segmentation_field3nodeCREATE INDEX idx_node_segmentation_field3
    ON node (segmentation_field3)x
EÅ#indexidx_node_segmentation_field2nodeCREATE INDEX idx_node_segmentation_field2
    ON node (segmentation_field2)x	EÅ#indexidx_node_segmentation_field1nodeCREATE INDEX idx_node_segmentation_field1
    ON node (segmentation_field1)`5Åindexidx_node_simple_namenode
CREATE INDEX idx_node_simple_name
    ON node (simple_name)Y1{indexidx_node_file_pathnode	CREATE INDEX idx_node_file_path
    ON node (file_path)P#windexidx_node_idnodeCREATE UNIQUE INDEX idx_node_id
    ON node (node_id)~%%Å?tableevent_recordevent_recordCREATE TABLE event_record (
                            file_path VARCHAR(500) NOT NULL
)Åh--Étableworkspace_recordworkspace_recordCREATE TABLE workspace_record (
                            stage VARCHAR(255) NOT NULL,
                            gmt_create INTEGER,
                            gmt_modified INTEGER
)É##Öetablefile_recordfile_recordCREATE TABLE file_record (
                      file_path VARCHAR(500) NOT NULL,
                      stage VARCHAR(255) NOT NULL,
                      file_state VARCHAR(255) NOT NULL,
                      tag VARCHAR(255),
                      gmt_create INTEGER,
                      gmt_modified INTEGER,
                      next_execute_time INTEGER
)Ç;ÑYtableedgeedgeCREATE TABLE edge (
                            source_id VARCHAR(255) NOT NULL,
                            target_id VARCHAR(255) NOT NULL,
                            edge_type Integer,
                            meta_data TEXT,
                            file_path VARCHAR(500) NOT NULL
)ÜãgtablenodenodeCREATE TABLE node (
                      node_id VARCHAR(255) NOT NULL,
                      node_type Integer NOT NULL,
                      package VARCHAR(255),
                      start_line INTEGER,
                      end_line INTEGER,
                      start_offset INTEGER,
                      end_offset INTEGER,
                      file_path VARCHAR(500) NOT NULL,
                      simple_name VARCHAR(255) NOT NULL,
                      meta_data TEXT,
                      segmentation_field1 VARCHAR(255),
                      segmentation_field2 VARCHAR(255),
                      segmentation_field3 VARCHAR(255),
                      segmentation_field4 VARCHAR(255),
                      lang VARCHAR(32)
)(Ìú                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        if not ean.isdigit():
            result['valid'] = False
            result['issue'] = "EAN must contain only digits"
            return result
        
        if len(ean) != 13:
            result['valid'] = False
            result['issue'] = f"EAN must be 13 digits, got {len(ean)}"
            return result
        
        # Validate checksum
        try:
            total = sum(int(ean[i]) * (3 if i % 2 else 1) for i in range(12))
            check_digit = (10 - (total % 10)) % 10
            if check_digit != int(ean[12]):
                result['valid'] = False
                result['issue'] = "Invalid EAN checksum"
        except:
            result['valid'] = False
            result['issue'] = "Error validating EAN checksum"
        
        return result

    def _validate_asin(self, asin: str) -> Dict[str, Any]:
        """Validate Amazon ASIN format."""
        result = {'valid': True, 'issue': ''}
        
        if not asin or not isinstance(asin, str):
            result['valid'] = False
            result['issue'] = "ASIN must be a non-empty string"
            return result
        
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            result['valid'] = False
            result['issue'] = f"Invalid ASIN format: {asin}"
        
        return result

    def _validate_sales_rank(self, rank: Any) -> Dict[str, Any]:
        """Validate sales rank value."""
        result = {'valid': True, 'issue': ''}
        
        if rank is None:
            return result  # Sales rank is optional
        
        try:
            rank_int = int(rank)
            if rank_int < 0: # Rank 0 is possible for new/unranked items, but negative is invalid
                result['valid'] = False
                result['issue'] = "Sales rank cannot be negative"
            elif rank_int > 20000000: # Arbitrary upper limit for sanity
                result['warnings'].append(f"Sales rank seems unrealistically high: {rank_int}")
        except (ValueError, TypeError):
            result['valid'] = False
            result['issue'] = f"Sales rank must be numeric, got: {type(rank).__name__}"
        
        return result

    def _validate_rating(self, rating: Any) -> Dict[str, Any]:
        """Validate product rating."""
        result = {'valid': True, 'issue': ''}
        
        if rating is None:
            return result  # Rating is optional
        
        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 5:
                result['valid'] = False
                result['issue'] = f"Rating must be between 0 and 5, got: {rating_float}"
        except (ValueError, TypeError):
            result['valid'] = False
            result['issue'] = f"Rating must be numeric, got: {type(rating).__name__}"
        
        return result

    def _is_text_restricted(self, text: str) -> bool:
        """Helper to check if a combined text contains restricted keywords."""
        if not text: return False
        text_lower = text.lower()
        for keyword in self.restricted_keywords:
            if keyword in text_lower:
                return True
        return False

    def _check_restricted_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if product contains restricted keywords in title or description."""
        # This method is now largely covered by _is_text_restricted and individual field validations
        # Kept for conceptual clarity if needed, but logic is integrated elsewhere.
        result = {'restricted': False, 'reason': ''}
        combined_text = str(product_data.get('title', '')) + " " + str(product_data.get('description', ''))
        if self._is_text_restricted(combined_text):
            result['restricted'] = True
            # Find first keyword for reason
            for keyword in self.restricted_keywords:
                if keyword in combined_text.lower():
                    result['reason'] = f"Product data contains restricted keyword: {keyword}"
                    break
        return result
        
    def _validate_financial_metrics(self, combined_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate financial calculations."""
        result = {'valid': True, 'warnings': []} # valid is always true, only warnings
        
        roi = combined_data.get('roi_percent_calculated', 0)
        profit = combined_data.get('estimated_profit_per_unit', 0)
        supplier_price = combined_data.get('supplier_product_info', {}).get('price', 0)
        amazon_price = combined_data.get('amazon_product_info', {}).get('current_price', 0)
        
        if not isinstance(supplier_price, (int, float)) or supplier_price <=0:
             result['warnings'].append(f"Supplier price is invalid for financial validation: {supplier_price}")
             return result # Cant do much more if supplier price is bad
        if not isinstance(amazon_price, (int, float)) or amazon_price <=0:
             result['warnings'].append(f"Amazon price is invalid for financial validation: {amazon_price}")
             # Can still check some things

        if roi > 1000 and profit > 0: # Only if profitable
            result['warnings'].append(f"Unusually high ROI: {roi}%")
        
        if profit > amazon_price * 0.8 and amazon_price > 0: # Avoid division by zero
            result['warnings'].append(f"Profit margin (¬£{profit:.2f}) seems very high compared to Amazon price (¬£{amazon_price:.2f})")
        
        if supplier_price > amazon_price and amazon_price > 0 : # Only if amazon price is valid
            result['warnings'].append(f"Supplier price (¬£{supplier_price:.2f}) higher than Amazon price (¬£{amazon_price:.2f})")
        
        if profit < 0 and roi > 0:
            result['warnings'].append(f"Contradictory financials: Negative profit (¬£{profit:.2f}) but positive ROI ({roi}%)")

        return result

    def _validate_text_field(self, text: Optional[str], field_name: str, min_length: int = 1, max_length: int = 5000, allow_empty: bool = False, restricted_keywords_check: bool = False) -> Dict[str, Any]:
        """Generic validation for a text field."""
        result = {'valid': True, 'issues': [], 'warnings': []}
        
        if text is None:
            if not allow_empty:
                result['valid'] = False
                result['issues'].append(f"{field_name} cannot be None")
            return result

        if not isinstance(text, str):
            result['valid'] = False
            result['issues'].append(f"{field_name} must be a string, got {type(text).__name__}")
            return result

        if not allow_empty and not text.strip():
            result['valid'] = False
            result['issues'].append(f"{field_name} cannot be empty or just whitespace")
            return result
        
        text_len = len(text)
        if not allow_empty and text_len < min_length:
            result['valid'] = False
            result['issues'].append(f"{field_name} too short (minimum {min_length} characters), got {text_len}")
        
        if text_len > max_length:
            result['warnings'].append(f"{field_name} very long (over {max_length} characters), got {text_len}")

        if restricted_keywords_check:
            if self._is_text_restricted(text): # Use helper
                 result['warnings'].append(f"{field_name} contains restricted keyword(s).")
        
        return result

    def _validate_image_urls(self, image_urls: Optional[List[str]], field_name: str = "images") -> Dict[str, Any]:
        """Validate a list of image URLs."""
        result = {'valid': True, 'issues': [], 'warnings': []}
        
        if image_urls is None:
            result['warnings'].append(f"{field_name} list is None (optional field)")
            return result 

        if not isinstance(image_urls, list):
            result['valid'] = False
            result['issues'].append(f"{field_name} must be a list, got {type(image_urls).__name__}")
            return result

        if not image_urls: 
            result['warnings'].append(f"No {field_name} provided (optional field).")
            return result

        for i, url in enumerate(image_urls):
            url_validation = self._validate_url(url)
            if not url_validation['valid']:
                result['valid'] = False 
                result['issues'].append(f"Invalid URL for {field_name}[{i}]: {url_validation['issues'][0]}")
            
            if not re.search(r'\.(jpeg|jpg|gif|png|webp)(\?.*)?$', str(url), re.IGNORECASE): # Ensure url is str
                result['warnings'].append(f"Image URL for {field_name}[{i}] ('{str(url)[:50]}...') does not have a common image extension.")
        
        return result

    def _validate_extracted_weight(self, weight_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the structure and values of extracted weight data."""
        result = {'valid': True, 'issues': [], 'warnings': []}
        if weight_data is None:
            result['warnings'].append("Weight data is missing (optional field)")
            return result

        if not isinstance(weight_data, dict):
            result['valid'] = False
            result['issues'].append(f"Weight data must be a dict, got {type(weight_data).__name__}")
            return result

        required_keys = ['value', 'unit', 'pounds']
        missing_keys = [key for key in required_keys if key not in weight_data]
        if missing_keys:
            result['valid'] = False
            result['issues'].append(f"Weight data missing key(s): {', '.join(missing_keys)}")
        
        if not result['valid']: return result

        value = weight_data.get('value')
        unit = weight_data.get('unit')
        pounds = weight_data.get('pounds')

        if not isinstance(value, (int, float)) or value <= 0:
            result['valid'] = False
            result['issues'].append(f"Weight value must be a positive number, got {value}")
        if not isinstance(unit, str) or not unit.strip():
            result['valid'] = False
            result['issues'].append(f"Weight unit must be a non-empty string, got {unit}")
        if not isinstance(pounds, (int, float)) or pounds <= 0:
            result['valid'] = False
            result['issues'].append(f"Weight in pounds must be a positive number, got {pounds}")
        
        if pounds < self.weight_limits['min_pounds']:
            result['warnings'].append(f"Weight {pounds:.2f} lbs is below minimum {self.weight_limits['min_pounds']} lbs")
        if pounds > self.weight_limits['max_pounds']:
            result['valid'] = False 
            result['issues'].append(f"Weight {pounds:.2f} lbs exceeds maximum {self.weight_limits['max_pounds']} lbs (FBA limit)")
            
        return result

    def _validate_extracted_dimensions(self, dimension_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the structure and values of extracted dimension data."""
        result = {'valid': True, 'issues': [], 'warnings': []}
        if dimension_data is None:
            result['warnings'].append("Dimension data is missing (optional field)")
            return result

        if not isinstance(dimension_data, dict):
            result['valid'] = False
            result['issues'].append(f"Dimension data must be a dict, got {type(dimension_data).__name__}")
            return result

        required_keys = ['length', 'width', 'height', 'unit', 'inches']
        missing_keys = [key for key in required_keys if key not in dimension_data]
        if missing_keys:
            result['valid'] = False
            result['issues'].append(f"Dimension data missing key(s): {', '.join(missing_keys)}")

        if not result['valid']: return result

        length = dimension_data.get('length')
        width = dimension_data.get('width')
        height = dimension_data.get('height')
        unit = dimension_data.get('unit')
        inches_tuple = dimension_data.get('inches')

        dim_values = {'length': length, 'width': width, 'height': height}
        for name, val in dim_values.items():
            if not isinstance(val, (int, float)) or val <= 0:
                result['valid'] = False
                result['issues'].append(f"Dimension {name} must be a positive number, got {val}")
        
        if not isinstance(unit, str) or not unit.strip():
            result['valid'] = False
            result['issues'].append(f"Dimension unit must be a non-empty string, got {unit}")

        if not isinstance(inches_tuple, tuple) or len(inches_tuple) != 3 or not all(isinstance(d, (int, float)) and d > 0 for d in inches_tuple):
            result['valid'] = False
            result['issues'].append(f"Dimensions in inches must be a tuple of 3 positive numbers, got {inches_tuple}")
        else:
            l_in, w_in, h_in = inches_tuple
            dims_sorted = sorted([l_in, w_in, h_in])
            longest_side = dims_sorted[2]
            median_side = dims_sorted[1]
            shortest_side = dims_sorted[0]

            if longest_side > self.dimension_limits['max_length_inches']:
                result['valid'] = False 
                result['issues'].append(f"Longest dimension {longest_side:.2f} inches exceeds FBA max length {self.dimension_limits['max_length_inches']} inches")
            
            girth = longest_side + 2 * (median_side + shortest_side)
            if girth > self.dimension_limits['max_girth_inches']:
                result['valid'] = False 
                result['issues'].append(f"Girth {girth:.2f} inches (L + 2*(W+H)) exceeds FBA max girth {self.dimension_limits['max_girth_inches']} inches")

            for d_val, d_name_suffix in zip(inches_tuple, ["length", "width", "height"]):
                 dim_name = f"{d_name_suffix}_inches"
                 if d_val < self.dimension_limits['min_inches']:
                     result['warnings'].append(f"Dimension {dim_name} {d_val:.2f} inches is below minimum {self.dimension_limits['min_inches']} inches")
        return result

    def generate_validation_report(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary report from multiple validation results.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            Summary report
        """
        total = len(validation_results)
        valid_count = sum(1 for r in validation_results if r.get('valid', False)) # Use .get for safety
        
        all_issues: List[str] = []
        all_warnings: List[str] = []
        quality_scores: List[float] = []
        
        for res in validation_results:
            all_issues.extend(res.get('issues', []))
            all_warnings.extend(res.get('warnings', []))
            quality_scores.append(res.get('data_quality_score', 0.0)) # Default to 0.0
        
        issue_counts: Dict[str, int] = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        warning_counts: Dict[str, int] = {}
        for warning in all_warnings:
            warning_counts[warning] = warning_counts.get(warning, 0) + 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_products_validated': total,
            'valid_products_count': valid_count,
            'invalid_products_count': total - valid_count,
            'overall_validation_rate_percent': (valid_count / total * 100) if total > 0 else 0,
            'average_data_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'common_issues_top_10': sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'common_warnings_top_10': sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'data_quality_score_distribution': {
                'excellent_90_plus': sum(1 for s in quality_scores if s >= 90),
                'good_70_89': sum(1 for s in quality_scores if 70 <= s < 90),
                'fair_50_69': sum(1 for s in quality_scores if 50 <= s < 70),
                'poor_below_50': sum(1 for s in quality_scores if s < 50)
            }
        }
        
        return report