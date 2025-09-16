Of course. Based on the provided files and conversation, I have synthesized, reorganized, and updated the content into a single, comprehensive master behavior specification.

This new document uses the superior, detailed, and final logic from `toroganize.md` while maintaining the professional structure and thoroughness of the original `AMAZON_FBA_SYSTEM_MASTER_BEHAVIOR_SPECIFICATION.md`. All final decisions—such as the queue split, write-once denominators, `system_progression` as the single source of truth, and non-sticky completion—are now codified in their correct place.

Here is the final, reorganized Markdown file:

---

# Amazon FBA Agent System - Master Behavior Specification

**Document Type**: Complete System Behavior Guide
**Version**: v3.8+ (Updated with Implementation Analysis)
**Date**: August 23, 2025
**Status**: Production Ready - Master Reference (Updated)
**Purpose**: Definitive guide for system behavior, processing flow, data management, and operational guarantees.

**🚨 IMPLEMENTATION STATUS UPDATE**: This document has been updated to reflect the latest system analysis findings, including identified implementation gaps, fixes applied, and remaining work items as of August 23, 2025. **Recent improvements include enhanced filter transparency logging with specification compliance.**

---

## 🎯 **EXECUTIVE SUMMARY**

The Amazon FBA Agent System v3.8+ is a production-ready automation platform that processes supplier websites to identify profitable Amazon FBA opportunities. 

**🚨 CRITICAL ARCHITECTURE NOTE**: The system contains **TWO DISTINCT WORKFLOWS** in `passive_extraction_workflow_latest.py`:

1. **🔄 Hybrid Processing Mode** (Primary/Recommended): `_run_hybrid_processing_mode()`
   - Completes both supplier extraction AND Amazon analysis for one category before proceeding to the next
   - Supports chunked, sequential, and balanced processing sub-modes
   - **This specification primarily documents the HYBRID mode workflow**

2. **📋 Regular/Legacy Workflow Mode**: Standard sequential processing
   - Extracts ALL supplier products first, then analyzes ALL products
   - Older implementation maintained for compatibility
   - Less efficient and not the focus of this specification

**⚠️ IMPORTANT**: When testing, implementing, or debugging, ensure you are working with the **HYBRID PROCESSING MODE** as it is the primary workflow described in this document.

**Core Architecture**: The system (in hybrid mode) is built on a set of deterministic principles to ensure reliability and data integrity. A single state object, `system_progression`, is the exclusive source of truth for resuming interrupted sessions. Data routing is managed by O(1) hash-based lookups, and all critical file I/O is protected by atomic save operations to prevent data corruption. This specification codifies the exact behavior, data contracts, and operational guarantees required for production deployment.

---

## 📊 **IMPLEMENTATION STATUS & ANALYSIS SUMMARY**

### **🔄 DUAL WORKFLOW ARCHITECTURE**

**CRITICAL SPECIFICATION CLARIFICATION**: The `passive_extraction_workflow_latest.py` contains **TWO SEPARATE WORKFLOW IMPLEMENTATIONS**:

#### **1. 🔄 Hybrid Processing Mode** (Primary - Focus of This Specification)
- **Method**: `_run_hybrid_processing_mode()`
- **Enabled When**: `config["hybrid_processing"]["enabled"] = true`
- **Processing Pattern**: Category-by-category completion (supplier → Amazon analysis → next category)
- **Sub-modes Available**:
  - **Chunked Mode**: `chunk_size_categories = 1` (most common)
  - **Balanced Mode**: Extract in batches, analyze each batch
  - **Sequential Mode**: Complete supplier extraction, then Amazon analysis
- **State Management**: Uses `system_progression` for phase-aware resumption
- **Compliance Status**: 🟡 Partially compliant with this specification

#### **2. 📋 Regular/Legacy Workflow Mode** (Secondary - Not Focus of This Specification)
- **Method**: Standard workflow methods (non-hybrid)
- **Enabled When**: `config["hybrid_processing"]["enabled"] = false`
- **Processing Pattern**: Extract ALL products first, then analyze ALL products
- **Legacy Implementation**: Maintained for backward compatibility
- **Compliance Status**: ❌ Not covered by this specification

**🚨 TESTING & IMPLEMENTATION NOTE**: 
- When testing resumption, manifests, filtering, or any feature described in this document
- **ALWAYS ensure `hybrid_processing.enabled = true`** in your system configuration
- **ALWAYS verify you're working with `_run_hybrid_processing_mode()`**
- The analysis in this document **ONLY applies to the HYBRID mode workflow**

### **✅ VERIFIED CORRECT IMPLEMENTATIONS**

| Component | Status | Details |
|-----------|--------|----------|
| **Filter Order** | ✅ **CORRECT** | LM → Cache → Extract sequence properly implemented in `utils/url_filter.py` |
| **Verbose Logging** | ✅ **FIXED** | Removed debug spam: `📊 Supplier data cached` and `--- Amazon analysis X/Y` logs |
| **Hash Optimization** | ✅ **WORKING** | O(1) lookups implemented with proper rebuild triggers |
| **Atomic Persistence** | ✅ **WORKING** | Windows Save Guardian used for critical saves |
| **Basic Filtering** | ✅ **WORKING** | Core filtering logic correctly separates skip/amazon/full categories |
| **Filter Transparency Logging** | ✅ **IMPLEMENTED** | Enhanced logging format with specification compliance |

### **🆕 RECENT IMPROVEMENTS IMPLEMENTED (August 23, 2025)**

#### **Filter Transparency & Logging Enhancement**
**Status**: ✅ **COMPLETED**  
**Files Modified**: `tools/passive_extraction_workflow_latest.py` (Lines 4385-4391)  
**Impact**: Enhanced system observability and specification compliance

**Improvements Made**:
1. **Enhanced Log Format**: Updated filter transparency messages for better clarity
   - **Before**: `🔗 Linking-map skip: 150`
   - **After**: `🔗 Linking-map check: 150 complete (skipped)`

2. **Combined Context Messages**: Improved product cache status reporting
   - **Before**: `💾 Product-cache (amazon-only): 45`
   - **After**: `💾 Product-cache check: 45 have supplier data; 25 need supplier extraction`

3. **Specification Compliance**: Filter invariant logging now matches documentation
   - **Before**: `🧮 Filter invariant: in=220 vs parts=220`
   - **After**: `🧮 Filter Invariant: in=220 == skip+amz_only+full=220`

4. **Additional Safety Check**: Redundant category completion validation
   - Added duplicate completion logic for enhanced reliability
   - Uses extracted variables for consistent logic flow

**Benefits Achieved**:
- ✅ **Enhanced Debugging**: More descriptive log messages aid troubleshooting
- ✅ **Specification Compliance**: Output matches project documentation requirements
- ✅ **Code Maintainability**: Variable extraction improves readability
- ✅ **System Reliability**: Additional safety checks prevent edge case issues
- ✅ **Zero Risk**: No impact on core functionality or processing calculations

### **🚨 CRITICAL IMPLEMENTATION GAPS IDENTIFIED**

| Component | Status | Impact | Root Cause Analysis |
|-----------|--------|--------|---------------------|tal Categories Count
🚨 CRITICAL ISSUE IDENTIFIED
Problem Description
Issue: Processing state shows incorrect total categories count

Current Value: "total_categories": 119
Expected Value: ~233 categories
Impact: 🔴 Critical - Affects progress calculations, user display metrics, and resumption logic accuracy
System Impact Analysis
This discrepancy affects several critical system components:

Progress Calculations: Incorrect percentage displays to users
Breadcrumb Logging: Wrong category index ratios (e.g., "cat_idx=50/119" instead of "cat_idx=50/233")
State Management: Potential resumption logic issues
User Experience: Misleading progress information
🔍 INVESTIGATION REQUIREMENTS
Root Cause Analysis Tasks
The following investigation must be performed to identify the source of the incorrect count:

1. Configuration Source Analysis
Examine: c{
  "asin_from_details": "B09DQ8T3ZZ",
  "title": "Spear Jackson Heavy Duty Sink and Drain Unblocker Gel - Powerful Formula- Indoor and Outdoor, 5 l (Pack of 1)",
  "current_price": 20.99,
  "amazon_monthly_sales_badge": 800,
  "main_image": "https://m.media-amazon.com/images/I/61V6bIrKnXL._AC_SL1460_.jpg",
  "thumbnails": [
    "https://m.media-amazon.com/images/I/41drVqbESNL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/51TJLcBUBeL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/51KNh8KVkEL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/41DffRuNV3L._AC_SR38,50_.jpg"
  ],
  "high_res_gallery": [],
  "amazon_product_details_section": {
    "ASIN": "B09DQ8T3ZZ",
    "Date First Available": "16 April 2021"
  },
  "date_first_available_from_details": "16 April 2021",
  "prime_eligible": true,
  "fulfilled_by_amazon": false,
  "seller_info_text": "Assured Products Limited",
  "sold_by_amazon": false,
  "rating": 4.1,
  "review_count": 723,
  "availability_text": "In stock",
  "in_stock": true,
  "features": [
    "SPEAR & JACKSON CLEANING PRODUCTS: Since 1760 Spear and Jackson has been selling hand, garden, contractors, agricultural, landscaping and professional tools from its base in the city of Sheffield. Their range of cleaning products are made to target tough stains, grease, grim and fat. Their Heavy Duty Outdoor Drain Unblocker Gel is designed to clear any deposits that are blocking your sink, leaving it draining smoothly",
    "SINK UNBLOCKER LIQUID GEL: Spear and Jackson's Heavy Duty Sink And Drain Unblocker comes in gel form and is designed to dissolve the fat, food, hair or soap residue build up that's blocking your sink. Their heavy duty sink and drain unblocker gel will instantly clear and dissolve the unwanted blockage, and with the sink freshener element of the gel, your sink will be look and smell brand new",
    "BATHROOM & KITCHEN SINK UNBLOCKER: With no drain snake require, this product really couldn't be any easier to use. The gel will dissolve any build up that is causing a blockage in your sink or drain in 3 hours. Ideal for the kitchen or bathroom sink, however this Heavy Duty Sink & Drain Unblocker works on exterior drains just as well. In comparison to other drain cleaners and unblockers on the market, this product has a powerful formulation that achieves results in rapid speed",
    "BATHROOM CLEANING PRODUCTS: Spear and Jackson's fast acting, powerful and effective sink and drain unblocker liquid is perfectly safe to use on all pipe types. For the best results, pour the heavy duty drain unblocker down the plughole, leave for a minimum of 3 hours (preferably overnight) and finish off by flushing the drain with hot water for at least 2 minutes to completely free any blockages - it's really that easy!",
    "SPEAR & JACKSON: With over 250 years experience and continuous innovation, Spear and Jackson have built an enviable reputation with their market leading products that offer high quality performance tools to suit a wide range of needs. Whether you're looking to unblock your sink drain or a concentrated mould, algae and moss spray then shop Spear and Jackson range of versatile, effective and long lasting cleaning products"
  ],
  "description": "Product description Sink &amp; Drain Unblocker Gel quickly clears drains and plug holes, dissolving hair, soap, grease and food deposits, the common causes of blockages even through standing water. Regular use maintains free running and keeps drains fresh. Contents: 1 x 5L Drain Unblocker. Directions Pour the heavy duty drain unblocker down the plughole, leave for a minimum of 3 hours (preferably overnight), then finish off by flushing the drain with hot water for at least 2 minutes. Safety Warning Keep away from the reach of kids. Legal Disclaimer Note: The colour of the bottle may vary See more",
  "specifications_table": {
    "Units": "‎5000.0 millilitre",
    "Brand": "‎Spear & Jackson",
    "Manufacturer": "‎Assured Products Limited",
    "Country of origin": "‎United Kingdom"
  },
  "selleramp": {
    "status": "SellerAmp extraction disabled"
  },
  "keepa": {
    "status": "Extraction process completed",
    "sales_rank_details_table": {
      "main_cat_current_rank": 3494,
      "main_cat_name": "Grocery 47 drops / month",
      "sub_cat_current_rank": 22,
      "sub_cat_name": "Drain Openers 3"
    },
    "ai_graph_analysis_status": "Keepa Graph AI Analysis disabled",
    "product_details_tab_data": {
      "Title": "Spear Jackson Heavy Duty Sink and Drain Unblocker Gel - Powerful Formula- Indoor and Outdoor, 5 l (Pack of 1)",
      "Sales Rank - Reference": "Grocery",
      "Sales Rank - Display Group": "grocery_display_on_website",
      "Bought in past month": "800+",
      "Reviews - Rating": 4.1,
      "Reviews - Rating Count": 723.0,
      "Last Price Change": "13 days ago",
      "Buy Box Seller": "Assured Products Limited (86% positive over last 12 months)",
      "Lowest FBM Seller": "Assured Products Limited (86% positive over last 12 months)",
      "Total Offer Count": "1",
      "Tracking since": "2021/09/01",
      "Listed since": "2021/04/16",
      "Categories - Root": "Grocery",
      "Categories - Sub": "Drain Openers",
      "Categories - Tree": "Grocery › Home Care & Cleaning › Household Cleaners › Drain Openers",
      "Website Display Group - Name": "Grocery",
      "ASIN": "B09DQ8T3ZZ",
      "Product Codes - EAN": "5060744384106",
      "Type": "DRAIN_OPENER_SUBSTANCE",
      "Manufacturer": "Assured Products Limited",
      "Brand": "Spear & Jackson",
      "Brand Store Name": "Spear & Jackson",
      "Brand Store URL Name": "SpearJackson",
      "Brand Store URL": "https://www.amazon.com/stores/SpearJackson/page/65ACE97A-B00B-48FC-B40D-6AC185CF94CB",
      "Product Group": "Grocery",
      "Color": "5 l (Pack of 1)",
      "Size": "5 l (Pack of 1)",
      "Unit Details - Unit Value": "5000",
      "Unit Details - Unit Type": "millilitre",
      "Scent": "Unscented",
      "Product Benefit": "Dissolves various types of blockages and freshens sinks",
      "Number of Items": "1",
      "Safety Warning": "Keep away from the reach of kids.",
      "Hazardous Materials": "Proper Shipping Name: United Nations Regulatory Id: Regulatory Packing Group: CORROSIVE LIQUID, N.O.S., CORROSIVE LIQUID, N.O.S. (CONTAINS SODIUM HYDROXIDE, SODIUM HYPOCHLORITE)UN1760II(more values available, copy cell to get all)"
    }
  },
  "eans_on_page": [
    "5060744384106"
  ],
  "ean_on_page_source": "Keepa_Product_Details",
  "ean_on_page": "5060744384106",
  "sales_rank": 3494,
  "category": "Grocery 47",
  "sales_rank_source": "Keepa_SalesRankDetailsTable",
  "estimated_monthly_sales_from_bsr": 200,
  "asin_extracted_from_page": "B09DQ8T3ZZ",
  "asin_queried": "B09DQ8T3ZZ",
  "asin": "B09DQ8T3ZZ",
  "_search_method_used": "title"
}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    {
  "asin_from_details": "B09ZV2DX8S",
  "title": "Egg Slicer, Heavy Duty Metal Egg Slicer Cutter for Boiled Eggs Dishwasher Safe, Manual Eggs Slicer Cutting Wire Made of Stainless Steel for Kitchen",
  "current_price": 9.99,
  "original_price": 12.99,
  "amazon_monthly_sales_badge": 600,
  "main_image": "https://m.media-amazon.com/images/I/81dpZDcAQKL._AC_SL1500_.jpg",
  "thumbnails": [
    "https://m.media-amazon.com/images/I/51cnB1XuBQL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/51BrZ-VRbxL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/5180jPbXAuL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/51Yhj7N8W+L._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/517vXuu2afL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/51CjhawizuL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/91XVEXaMfDL._SL1500_PKplay-button-mb-image-grid-small_.jpg"
  ],
  "high_res_gallery": [],
  "prime_eligible": true,
  "fulfilled_by_amazon": false,
  "seller_info_text": "SD E-commerce",
  "sold_by_amazon": false,
  "rating": 4.7,
  "review_count": 701,
  "availability_text": "In stock",
  "in_stock": true,
  "features": [
    "Metal Egg Slicer: This egg slicer evenly cuts hard boiled eggs into slices and wedges, helping you garnish your salads and sandwiches with hard boiled eggs in seconds. This egg slicer slices eggs easier and safer than a knife, making food preparation easier.",
    "Multipurpose Egg Slicer This 2-in-1 egg slicer not only works with hard-boiled eggs, it also works well with strawberries, mushrooms, kiwi and other soft fruits and is the perfect addition to any fruit salad. No mess. No mush, no sharp knives, it's a versatile addition to any home cook's arsenal.",
    "Durable Material Each egg slicer cutting wire is made of food grade stainless steel, sharp and rustproof. The bottom of the egg slicer is made of ABS plastic which is galvanized, making it durable and sturdy.",
    "Easy to Clean and Use: This egg slicer is easy to use, just put the boiled egg on the base, put the cutting wire, and you're done! The smooth bottom of the egg slicer is easy to clean manually and is dishwasher safe. This egg slicer will not spend most of your time cleaning."
  ],
  "description": "Product Description If you love hard boiled eggs but can't cut them, you need an egg slicer in your arsenal of kitchen gadgets. With this versatile egg slicer you can quickly and easily prepare beautiful dishes. This egg slicer quickly and evenly slices peeled, hard-boiled eggs with sharp precision, easier and safer to use than a knife. To use the egg slicer, simply place an egg in the base, choose a cutting plate and press down over the food to be sliced. which has sharp wires that do the cutting, with one gentle motion you're done. Easy handling: Step 1: Peel the hard-boiled eggs. Step 2: Place the shelled eggs in the center of the cutting board. Step 3: Press the edge of the egg slicer surface firmly over the plate with your thumbs. Repeat these steps for several more eggs at a time. Stainless Steel Cutting Wires These egg slicer cutting wires are made of stainless steel, make it sharp and anti-rust. It cut hard boiled eggs evenly and help you add hard boiled egg toppings to your salads and sandwiches in seconds. Made of Durable Metal The egg slicer's whole body is made of cast aluminum. Dishwasher Safe This egg slicer is designed to be easy to clean and dishwasher safe, saving you time cleaning up after meal prep.",
  "specifications_table": {
    "Brand Name": "Thimmamma",
    "Recommended Uses For Product": "Egg",
    "Manufacturer": "Thimmamma",
    "UPC": "774882114123",
    "Customer Reviews": "4.7 4.7 out of 5 stars (701) var dpAcrHasRegisteredArcLinkClickAction; P.when('A', 'ready').execute(function(A) { if (dpAcrHasRegisteredArcLinkClickAction !== true) { dpAcrHasRegisteredArcLinkClickAction = true; A.declarative( 'acrLink-click-metrics', 'click', { \"allowLinkDefault\": true }, function (event) { if (window.ue) { ue.count(\"acrLinkClickCount\", (ue.count(\"acrLinkClickCount\") || 0) + 1); } } ); } }); P.when('A', 'cf').execute(function(A) { A.declarative('acrStarsLink-click-metrics', 'click', { \"allowLinkDefault\" : true }, function(event){ if(window.ue) { ue.count(\"acrStarsLinkWithPopoverClickCount\", (ue.count(\"acrStarsLinkWithPopoverClickCount\") || 0) + 1); } }); }); 4.7 out of 5 stars",
    "ASIN": "B09ZV2DX8S",
    "Item Type Name": "Boiled Egg Slicer",
    "Included Components": "Egg Slicer",
    "Item height": "3 centimetres"
  },
  "selleramp": {
    "status": "SellerAmp extraction disabled"
  },
  "keepa": {
    "status": "Extraction process completed",
    "sales_rank_details_table": {
      "main_cat_current_rank": 4717,
      "main_cat_name": "Home & Kitchen 30 drops / month",
      "sub_cat_current_rank": 2,
      "sub_cat_name": "Egg Cutters 5"
    },
    "ai_graph_analysis_status": "Keepa Graph AI Analysis disabled",
    "product_details_tab_data": {
      "Title": "Egg Slicer, Heavy Duty Metal Egg Slicer Cutter for Boiled Eggs Dishwasher Safe, Manual Eggs Slicer Cutting Wire Made of Stainless Steel for Kitchen",
      "Sales Rank - Reference": "Home & Kitchen",
      "Sales Rank - Display Group": "kitchen_display_on_website",
      "Bought in past month": "600+",
      "Reviews - Rating": 4.7,
      "Reviews - Rating Count": 701.0,
      "Last Price Change": "2 days ago",
      "Buy Box Seller": "SD E-commerce (97% positive over last 12 months)",
      "Lowest FBA Seller": "SD E-commerce (97% positive over last 12 months) George Savage Store (99% positive over last 12 months)",
      "FBA Pick&Pack Fee": 2.42,
      "Referral Fee %": "15.02 %",
      "Referral Fee based on current Buy Box price": 1.5,
      "Total Offer Count": "2",
      "Tracking since": "2022/05/16",
      "Listed since": "2022/05/09",
      "Categories - Root": "Home & Kitchen",
      "Categories - Sub": "Egg Cutters",
      "Categories - Tree": "Home & Kitchen › Cooking & Dining › Kitchen Tools & Gadgets › Peeling, Grating & Slicing Tools › Mandolines & Slicers › Egg Cutters",
      "Website Display Group - Name": "Kitchen",
      "ASIN": "B09ZV2DX8S",
      "Product Codes - UPC": "774882114123",
      "Product Codes - EAN": "0774882114123",
      "Product Codes - PartNumber": "Egg Slicers 1pcs",
      "Parent ASIN": "B0B8JY2QNW",
      "Variation ASINs": "B0CHF13CXP, B0C58MG3VF, B09ZV2DX8S",
      "Type": "FOOD_SLICER",
      "Manufacturer": "Thimmamma",
      "Brand": "Thimmamma",
      "Brand Store Name": "Thimmamma",
      "Brand Store URL Name": "Thimmamma",
      "Brand Store URL": "https://www.amazon.com/stores/Thimmamma/page/AC3F8EBB-608C-474A-A2B0-13D72A180669",
      "Product Group": "Kitchen",
      "Model": "Egg Slicers 1pcs",
      "Color": "Silver",
      "Size": "13.5 x 8 cm",
      "Style": "egg slicer",
      "Material": "Metal",
      "Recommended Uses": "Egg",
      "Languages": "English",
      "Videos - Video Count": "1",
      "Videos - Main Videos": "Creator: Main, https://m.media-amazon.com/images/I/91XVEXaMfDL.jpg, https://m.media-amazon.com/images/S/vse-vms-transcoding-artifact-eu-west-1-prod/5032e9c6-5890-49e8-9861-5faa6caf6694/default.jobtemplate.hls.m3u8",
      "Package - Dimension (cm³)": "14.0 x 8.7 x 3.7 cm (= 451 cm³ )",
      "Package - Weight (g)": "160",
      "Package - Quantity": "1",
      "Item - Dimension (cm³)": "13.5 x 8.0 x 3.0 cm (= 324 cm³ )",
      "Item - Model (g)": "150"
    }
  },
  "eans_on_page": [
    "0774882114123"
  ],
  "ean_on_page_source": "Keepa_Product_Details",
  "ean_on_page": "0774882114123",
  "sales_rank": 4717,
  "category": "Home & Kitchen 30",
  "sales_rank_source": "Keepa_SalesRankDetailsTable",
  "estimated_monthly_sales_from_bsr": 100,
  "asin_extracted_from_page": "B09ZV2DX8S",
  "asin_queried": "B09ZV2DX8S",
  "asin": "B09ZV2DX8S",
  "_search_method_used": "title"
}                                                                                                                                                         {
  "asin_from_details": "B00M377JTS",
  "title": "TML Rectangular Bowl 11L Glitter Red",
  "current_price": 6.38,
  "main_image": "https://m.media-amazon.com/images/I/51K8AvseecL._AC_SL1024_.jpg",
  "thumbnails": [
    "https://m.media-amazon.com/images/I/31LMZhJ1QbL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/21YESCvh-rL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/31fdsxkBC6L._SL1500_.jpg"
  ],
  "high_res_gallery": [],
  "prime_eligible": true,
  "fulfilled_by_amazon": false,
  "seller_info_text": "FINCHLEY ENTERPRISE",
  "sold_by_amazon": false,
  "rating": 3.7,
  "review_count": 43,
  "availability_text": "In stock",
  "in_stock": true,
  "features": [
    "Durable"
  ],
  "specifications_table": {
    "Brand Name": "TML",
    "Global Trade Identification Number": "05022092002255",
    "Customer Reviews": "3.7 3.7 out of 5 stars (43) var dpAcrHasRegisteredArcLinkClickAction; P.when('A', 'ready').execute(function(A) { if (dpAcrHasRegisteredArcLinkClickAction !== true) { dpAcrHasRegisteredArcLinkClickAction = true; A.declarative( 'acrLink-click-metrics', 'click', { \"allowLinkDefault\": true }, function (event) { if (window.ue) { ue.count(\"acrLinkClickCount\", (ue.count(\"acrLinkClickCount\") || 0) + 1); } } ); } }); P.when('A', 'cf').execute(function(A) { A.declarative('acrStarsLink-click-metrics', 'click', { \"allowLinkDefault\" : true }, function(event){ if(window.ue) { ue.count(\"acrStarsLinkWithPopoverClickCount\", (ue.count(\"acrStarsLinkWithPopoverClickCount\") || 0) + 1); } }); }); 3.7 out of 5 stars",
    "ASIN": "B00M377JTS",
    "Unit Count": "1.0 count"
  },
  "selleramp": {
    "status": "SellerAmp extraction disabled"
  },
  "keepa": {
    "status": "Extraction process completed",
    "sales_rank_details_table": {
      "main_cat_current_rank": 1345459,
      "main_cat_name": "Home & Kitchen",
      "sub_cat_current_rank": 1030,
      "sub_cat_name": "Dessert Bowls 6"
    },
    "ai_graph_analysis_status": "Keepa Graph AI Analysis disabled",
    "product_details_tab_data": {
      "Title": "TML Rectangular Bowl 11L Glitter Red",
      "Sales Rank - Reference": "Home & Kitchen",
      "Sales Rank - Display Group": "kitchen_display_on_website",
      "Reviews - Rating": 3.7,
      "Reviews - Rating Count": 43.0,
      "Last Price Change": "5 days ago",
      "Buy Box Seller": "FINCHLEY ENTERPRISE (86% positive over last 12 months)",
      "FBA Pick&Pack Fee": 5.16,
      "Referral Fee %": "15.05 %",
      "Referral Fee based on current Buy Box price": 0.96,
      "Lowest FBM Seller": "FINCHLEY ENTERPRISE (86% positive over last 12 months)",
      "Total Offer Count": "1",
      "Tracking since": "2017/03/28",
      "Listed since": "2014/08/28",
      "Categories - Root": "Home & Kitchen",
      "Categories - Sub": "Dessert Bowls",
      "Categories - Tree": "Home & Kitchen › Cooking & Dining › Tableware › Dishware & Serving Pieces › Dinnerware › Bowls › Dessert Bowls",
      "Website Display Group - Name": "Kitchen",
      "ASIN": "B00M377JTS",
      "Product Codes - EAN": "5022092002255",
      "Product Codes - PartNumber": "307655",
      "Type": "BUCKET",
      "Brand": "TML",
      "Product Group": "Home",
      "Model": "307655",
      "Color": "Red",
      "Size": "11L",
      "Unit Details - Unit Value": "1",
      "Unit Details - Unit Type": "count",
      "Pattern": "Solid",
      "Style": "Modern",
      "Binding": "Kitchen & Home",
      "Package - Dimension (cm³)": "37.2 x 30.6 x 13.4 cm (= 15,253 cm³ )",
      "Package - Weight (g)": "300",
      "Package - Quantity": "1",
      "Item - Model (g)": "300"
    }
  },
  "eans_on_page": [
    "5022092002255"
  ],
  "ean_on_page_source": "Keepa_Product_Details",
  "ean_on_page": "5022092002255",
  "sales_rank": 1345459,
  "category": "Home & Kitchen",
  "sales_rank_source": "Keepa_SalesRankDetailsTable",
  "estimated_monthly_sales_from_bsr": 5,
  "asin_extracted_from_page": "B00M377JTS",
  "asin_queried": "B00M377JTS",
  "asin": "B00M377JTS",
  "_search_method_used": "EAN"
}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       {
  "asin_from_details": "B09CDVYZVP",
  "title": "Cutacut Kitchen Scissors Stainless Steel Sharp Blades with TPR Grip - Multipurpose Kitchen Scissors Heavy Duty for Meat, Chicken, Fish, Vegetables, and Herbs – Bottle Opener. (Red)",
  "current_price": 19.99,
  "original_price": 39.99,
  "amazon_monthly_sales_badge": 100,
  "main_image": "https://m.media-amazon.com/images/I/6146R00C5UL._AC_SL1500_.jpg",
  "thumbnails": [
    "https://m.media-amazon.com/images/I/41sVcSUnW8L._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/51zPR2JenXL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/51m+qopZW2L._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/510wLXyZcjL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/41FGrdu24fL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/51vYOH7xNxL._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/51-8t5TU9NL._SL1500_PKplay-button-mb-image-grid-small_.jpg"
  ],
  "high_res_gallery": [],
  "prime_eligible": true,
  "fulfilled_by_amazon": false,
  "seller_info_text": "cut a cut",
  "sold_by_amazon": false,
  "rating": 4.6,
  "review_count": 1318,
  "availability_text": "In stock",
  "in_stock": true,
  "features": [
    "Ergonomic Design: Our perfectly designed meat scissor is extra smooth and comfortable for your hand. It won’t hurt you while using for a long time and will not leave any marks on your hand. It's also suitable for left and right hand",
    "Premium Quality: This scissors kitchen is made of stainless steel, with a perfect size of 21.5 cm. Our scissor is very fast while cutting, and our non-loosing strongly jointed pairs of blades make this one of the best kitchen tools",
    "Additional Features: Kitchen scissors dishwasher safe is rust-free with high-speed micro-serrated and water-resistant blades. We have added a cover to protect it against dirt for the blade’s safety. A careful inspection and testing make sure that you get high quality",
    "Built-in Opener: Our meat scissor kitchen scissor has a serrated section in the middle of the grip handle, which helps you open bottles and jars quickly. Even cracking nuts won’t be an issue with our additional feature",
    "Multiple Use: Cutacut poultry shears are perfect for different use, not only in the kitchen for cutting vegetables, herbs, or meat. You can also use it for gardening, opening sealed jars or bottles, and cracking any nuts"
  ],
  "description": "Product Description Multipurpose: You can use our 5 in 1 Scissor for various things like, chicken, vegetables, herbs etc Fish Scraper: scrap your fish skin without using slippery knives or chopping board Bottle Opener: Opens Bottle very easily and safely with our Bottle Blade Nut Cracker: A Nut cracker is included in the center of our Scissor Blades Cover: Blades cover is also available which will keep the scissor free from dirt and rust Gardening shears: Easily prunes plants and cuts small branches",
  "specifications_table": {
    "Brand": "CUTACUT",
    "UPC": "195893099634",
    "Customer Reviews": "4.6 4.6 out of 5 stars (1,318) var dpAcrHasRegisteredArcLinkClickAction; P.when('A', 'ready').execute(function(A) { if (dpAcrHasRegisteredArcLinkClickAction !== true) { dpAcrHasRegisteredArcLinkClickAction = true; A.declarative( 'acrLink-click-metrics', 'click', { \"allowLinkDefault\": true }, function (event) { if (window.ue) { ue.count(\"acrLinkClickCount\", (ue.count(\"acrLinkClickCount\") || 0) + 1); } } ); } }); P.when('A', 'cf').execute(function(A) { A.declarative('acrStarsLink-click-metrics', 'click', { \"allowLinkDefault\" : true }, function(event){ if(window.ue) { ue.count(\"acrStarsLinkWithPopoverClickCount\", (ue.count(\"acrStarsLinkWithPopoverClickCount\") || 0) + 1); } }); }); 4.6 out of 5 stars",
    "ASIN": "B09CDVYZVP",
    "Item Type Name": "Cutacut Kitchen Scissors Stainless Steel Sharp Blades with TPR Grip - Multipurpose Kitchen Scissors Heavy Duty for Meat, Chicken, Fish, Vegetables, and Herbs – Bottle Opener.",
    "Included Components": "no",
    "Item height": "1 centimetres",
    "Manufacturer": "cutacut",
    "Unit Count": "1.0 count"
  },
  "selleramp": {
    "status": "SellerAmp extraction disabled"
  },
  "keepa": {
    "status": "Extraction process completed",
    "sales_rank_details_table": {
      "main_cat_current_rank": 23728,
      "main_cat_name": "Home & Kitchen 14 drops / month",
      "sub_cat_current_rank": 29,
      "sub_cat_name": "Kitchen Scissors 3"
    },
    "ai_graph_analysis_status": "Keepa Graph AI Analysis disabled",
    "product_details_tab_data": {
      "Title": "Cutacut Kitchen Scissors Stainless Steel Sharp Blades with TPR Grip - Multipurpose Kitchen Scissors Heavy Duty for Meat, Chicken, Fish, Vegetables, and Herbs – Bottle Opener. (Red)",
      "Sales Rank - Reference": "Home & Kitchen",
      "Sales Rank - Display Group": "kitchen_display_on_website",
      "Bought in past month": "100+",
      "Reviews - Rating": 4.6,
      "Reviews - Rating Count": 1.0,
      "Last Price Change": "51 days ago",
      "Buy Box Seller": "cut a cut (94% positive over last 12 months)",
      "Lowest FBA Seller": "cut a cut (94% positive over last 12 months)",
      "FBA Pick&Pack Fee": 2.1,
      "Referral Fee %": "15.01 %",
      "Referral Fee based on current Buy Box price": 3.0,
      "Total Offer Count": "1",
      "Tracking since": "2022/04/04",
      "Listed since": "2021/08/11",
      "Categories - Root": "Home & Kitchen",
      "Categories - Sub": "Kitchen Scissors",
      "Categories - Tree": "Home & Kitchen › Cooking & Dining › Kitchen Tools & Gadgets › Kitchen Scissors",
      "Website Display Group - Name": "Home Improvement",
      "ASIN": "B09CDVYZVP",
      "Product Codes - UPC": "195893099634",
      "Product Codes - EAN": "0195893099634",
      "Product Codes - PartNumber": "1",
      "Parent ASIN": "B0C37T9KL3",
      "Variation ASINs": "B09CDVYZVP",
      "Type": "SCISSORS",
      "Manufacturer": "cutacut",
      "Brand": "CUTACUT",
      "Product Group": "Home Improvement",
      "Model": "kitchen Scissor Red",
      "Color": "Red",
      "Unit Details - Unit Value": "1",
      "Unit Details - Unit Type": "count",
      "Style": "RED",
      "Material": "Stainless Steel",
      "Number of Items": "1",
      "Videos - Video Count": "1",
      "Videos - Main Videos": "Creator: Main, https://m.media-amazon.com/images/I/51-8t5TU9NL.jpg, https://m.media-amazon.com/images/S/vse-vms-transcoding-artifact-eu-west-1-prod/fc21fa98-78a6-4b55-86e4-2116a07274cf/default.jobtemplate.hls.m3u8",
      "Package - Dimension (cm³)": "22.0 x 10.0 x 1.9 cm (= 418 cm³ )",
      "Package - Weight (g)": "150",
      "Package - Quantity": "1",
      "Item - Dimension (cm³)": "20.0 x 9.0 x 1.0 cm (= 180 cm³ )",
      "Included Components": "no"
    }
  },
  "eans_on_page": [
    "0195893099634"
  ],
  "ean_on_page_source": "Keepa_Product_Details",
  "ean_on_page": "0195893099634",
  "sales_rank": 23728,
  "category": "Home & Kitchen 14",
  "sales_rank_source": "Keepa_SalesRankDetailsTable",
  "estimated_monthly_sales_from_bsr": 20,
  "asin_extracted_from_page": "B09CDVYZVP",
  "asin_queried": "B09CDVYZVP",
  "asin": "B09CDVYZVP",
  "_search_method_used": "title"
}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               {
  "asin_from_details": "B095X1L2DY",
  "title": "HTS Motor & Cartridge Compatible with BAXI NETA TEC Motor & Cartridge 720064401 & 720448601",
  "current_price": 48.0,
  "main_image": "https://m.media-amazon.com/images/I/51TaEsSIApS._AC_SL1500_.jpg",
  "thumbnails": [
    "https://m.media-amazon.com/images/I/31wBR8zJ45S._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/31FS6+kdwrS._SL1500_.jpg",
    "https://m.media-amazon.com/images/I/3135-42KaLS._SL1500_.jpg"
  ],
  "high_res_gallery": [],
  "amazon_product_details_section": {
    "ASIN": "B095X1L2DY",
    "Date First Available": "26 May 2021"
  },
  "date_first_available_from_details": "26 May 2021",
  "prime_eligible": false,
  "fulfilled_by_amazon": false,
  "seller_info_text": "National Boiler Spares",
  "sold_by_amazon": false,
  "rating": 5.0,
  "availability_text": "In stock",
  "in_stock": true,
  "features": [
    "Perfect Compatibility: Specifically designed to replace BAXI Neta Tec Motor & Cartridge models 720064401 and 720448601, ensuring a precise fit and reliable performance.",
    "Efficient Heating System Component: Optimizes the operation of your boiler’s motor and cartridge, ensuring consistent heating and hot water delivery.",
    "Durable Construction: Made from high-quality materials for long-lasting durability and resistance to wear, even in demanding heating systems.",
    "Enhanced Performance: Designed to improve the efficiency of the heating process, reducing energy consumption while maintaining system reliability.",
    "Easy Installation: Engineered for simple, hassle-free replacement, minimizing downtime and making it easier to restore your boiler’s performance.",
    "12-Month Warranty: Comes with a comprehensive 12-month warranty, providing peace of mind and ensuring the product’s reliability and quality."
  ],
  "description": "HTS Motor &amp; Cartridge (Compatible with BAXI Neta Tec Motor &amp; Cartridge 720064401 &amp; 720448601) The HTS Motor &amp; Cartridge is a high-quality replacement designed for BAXI Neta Tec boilers, offering seamless integration and efficient operation. This motor and cartridge assembly ensures reliable performance and optimal heating system functionality, keeping your BAXI boiler running smoothly for years.",
  "specifications_table": {
    "Manufacturer": "‎HTS",
    "Part Number": "‎720064401 720448601",
    "Item model number": "‎720064401 720448601",
    "Colour": "‎Black",
    "Material": "‎Plastic",
    "Item Package Quantity": "‎1"
  },
  "selleramp": {
    "status": "SellerAmp extraction disabled"
  },
  "keepa": {
    "status": "Extraction process completed",
    "sales_rank_details_table": {
      "main_cat_current_rank": 635023,
      "main_cat_name": "DIY & Tools 0.3 drops / month",
      "sub_cat_current_rank": 0,
      "sub_cat_name": "-1 0"
    },
    "ai_graph_analysis_status": "Keepa Graph AI Analysis disabled",
    "product_details_tab_data": {
      "Title": "HTS Motor & Cartridge Compatible with BAXI NETA TEC Motor & Cartridge 720064401 & 720448601",
      "Sales Rank - Reference": "DIY & Tools",
      "Sales Rank - Display Group": "home_improvement_display_on_website",
      "Last Price Change": "50 days ago",
      "Buy Box Seller": "National Boiler Spares (91% positive over last 12 months)",
      "Lowest FBM Seller": "National Boiler Spares (91% positive over last 12 months)",
      "Total Offer Count": "1",
      "Tracking since": "2021/07/02",
      "Listed since": "2021/05/26",
      "Categories - Root": "DIY & Tools",
      "Categories - Sub": "Accessories",
      "Categories - Tree": "DIY & Tools › Building Supplies › Heating & Cooling › Central Heating Systems & Accessories › Accessories",
      "Website Display Group - Name": "Home Improvement",
      "ASIN": "B095X1L2DY",
      "Product Codes - EAN": "5056511804250",
      "Product Codes - PartNumber": "720064401 720448601",
      "Freq. Bought Together": "B00GRR2LS4, B0CQ2WZ272",
      "Type": "BUILDING_MATERIAL",
      "Manufacturer": "HTS",
      "Brand": "HTS",
      "Brand Store Name": "HTS",
      "Brand Store URL Name": "NationalBoilerSpares",
      "Brand Store URL": "https://www.amazon.com/stores/NationalBoilerSpares/page/7ACACF07-B562-4FBC-9149-4BC293A3DDF9",
      "Product Group": "Home Improvement",
      "Model": "720064401 720448601",
      "Color": "Black",
      "Unit Details - Unit Value": "1",
      "Unit Details - Unit Type": "count",
      "Material": "Plastic",
      "Number of Items": "1",
      "Package - Quantity": "1"
    }
  },
  "eans_on_page": [
    "5056511804250"
  ],
  "ean_on_page_source": "Keepa_Product_Details",
  "ean_on_page": "5056511804250",
  "sales_rank": 635023,
  "category": "DIY & Tools 0.3",
  "sales_rank_source": "Keepa_SalesRankDetailsTable",
  "estimated_monthly_sales_from_bsr": 5,
  "asin_extracted_from_page": "B095X1L2DY",
  "asin_queried": "B095X1L2DY",
  "asin": "B095X1L2DY",
  "_search_method_used": "EAN"
}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     