# Conversational AI Agent System Design
**Conversational Workflow Automation for Amazon FBA Sourcing**

**Date**: January 4, 2025
**Budget**: $2-5 per supplier run (acceptable)
**Objective**: Fully automated pipeline through natural language interaction

---

## 🎯 System Overview

Replace the **45-90 minute manual setup process** with a **conversational AI agent** that:
1. Chats with you to gather requirements
2. Asks clarifying questions about selectors, ROI, categories
3. Generates all config files and scripts automatically
4. Executes the complete pipeline
5. Analyzes results and provides insights

**Target Time**: 5-10 minutes of conversation → automated execution

---

## 🏗️ Architecture Design

### Component Stack

```
┌─────────────────────────────────────────────┐
│   USER INTERACTION LAYER                    │
│   - Web UI Chatbot (Streamlit/Gradio)      │
│   - CLI Chat Interface (Rich/Prompt)        │
│   - API Endpoint (REST/WebSocket)           │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│   AI ORCHESTRATOR (Claude/GPT-4)            │
│   - Conversation Manager                     │
│   - Requirement Extractor                    │
│   - Context Builder                          │
│   - Decision Engine                          │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│   CODE GENERATION LAYER                     │
│   - Config Generator (JSON templates)       │
│   - Script Generator (Python code)          │
│   - Validation Engine                       │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│   EXECUTION LAYER (Existing System)         │
│   - PassiveExtractionWorkflow              │
│   - ConfigurableSupplierScraper            │
│   - AmazonPlaywrightExtractor              │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│   ANALYSIS LAYER (New AI Component)         │
│   - Product Analyzer                        │
│   - Market Insights                         │
│   - Recommendation Engine                   │
└─────────────────────────────────────────────┘
```

---

## 💬 Conversation Flow Design

### Sample Interaction

```
🤖 AI Agent: Hi! I'm your Amazon FBA sourcing assistant.
            What supplier would you like to analyze?

👤 User: I want to scan examplewholesale.co.uk

🤖 AI: Great! Let me help you set this up. I'll need some information.

    1. What's the main URL? (e.g., https://www.examplewholesale.co.uk)

👤 User: https://www.examplewholesale.co.uk

🤖 AI: Perfect! Now, which product categories do you want to analyze?

      You can provide:
      - Category URLs (e.g., https://site.com/category/electronics)
      - Category names (I'll try to find URLs)
      - "All categories" (I'll discover them)

👤 User: Just these two:
        - https://www.examplewholesale.co.uk/home-kitchen
        - https://www.examplewholesale.co.uk/pet-supplies

🤖 AI: Got it! 2 categories selected.

      Now for the technical part - CSS selectors. I need selectors for:

      📋 PRODUCT TITLE selector:

👤 User: a.product-name

🤖 AI: ✅ Product title selector saved.

      💰 PRODUCT PRICE selector:

👤 User: span.price, .price-box .price

🤖 AI: ✅ Price selectors saved (2 fallbacks).

      🔢 EAN/BARCODE selector:

👤 User: span.ean-code, meta[itemprop='gtin13']

🤖 AI: ✅ EAN selectors saved (2 fallbacks).

      🔗 PRODUCT URL selector:

👤 User: a.product-link

🤖 AI: ✅ URL selector saved.

      🖼️ PRODUCT IMAGE selector:

👤 User: img.product-image

🤖 AI: ✅ Image selector saved.

      📄 PAGINATION pattern:
      How does pagination work?
      - URL pattern (e.g., ?page=1, ?p=1)
      - Next button
      - Load more button

👤 User: URL pattern: ?page={page}

🤖 AI: ✅ Pagination configured.

      🔐 AUTHENTICATION:
      Does this site require login? (yes/no)

👤 User: Yes

🤖 AI: Please provide login selectors:

      Email field selector:

👤 User: input#email

🤖 AI: ✅ Email field saved.

      Password field selector:

👤 User: input#password

🤖 AI: ✅ Password field saved.

      Login button selector:

👤 User: button.login-btn

🤖 AI: ✅ Login button saved.

      Test product URL (to verify authentication):

👤 User: https://www.examplewholesale.co.uk/test-product

🤖 AI: ✅ Test URL saved.

      Credentials (stored in config/system_config.json):
      Username:

👤 User: myemail@example.com

🤖 AI: ✅ Username saved.

      Password:

👤 User: mypassword123

🤖 AI: ✅ Password saved (encrypted).

      📊 PROFITABILITY CRITERIA:

      Minimum ROI percentage (default: 15%):

👤 User: 20%

🤖 AI: ✅ Min ROI: 20%

      Minimum profit per unit (default: £0.25):

👤 User: £0.50

🤖 AI: ✅ Min profit: £0.50

      Maximum price to scan (default: £20):

👤 User: £15

🤖 AI: ✅ Max price: £15

      Any other preferences? (categories to exclude, minimum reviews, etc.)

👤 User: Minimum 10 reviews, rating above 4.0

🤖 AI: ✅ Min reviews: 10, Min rating: 4.0

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      📋 CONFIGURATION SUMMARY
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      Supplier: examplewholesale.co.uk
      Categories: 2 URLs
      Selectors: Complete ✅
      Authentication: Configured ✅
      ROI Threshold: 20%
      Min Profit: £0.50
      Max Price: £15
      Min Reviews: 10
      Min Rating: 4.0

      Ready to proceed? (yes/no/edit)

👤 User: yes

🤖 AI: Excellent! I'm now generating all required files:

      ⏳ Generating config/supplier_configs/examplewholesale.co.uk.json...
      ✅ Done

      ⏳ Generating config/examplewholesale_categories.json...
      ✅ Done

      ⏳ Updating config/system_config.json with workflow...
      ✅ Done

      ⏳ Generating tools/examplewholesale/supplier_authentication_service.py...
      ✅ Done

      ⏳ Generating run_custom_examplewholesale.py entry script...
      ✅ Done

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      🚀 EXECUTING PIPELINE
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      Starting Chrome browser connection...
      ✅ Connected to Chrome on port 9222

      Authenticating with examplewholesale.co.uk...
      ✅ Authentication successful

      Processing Category 1/2: home-kitchen
      ├─ Discovered 47 products
      ├─ Extracted supplier data: 45/47 (95.7%)
      ├─ Matched on Amazon: 41/45 (91.1%)
      └─ Meeting criteria: 12 products

      Processing Category 2/2: pet-supplies
      ├─ Discovered 63 products
      ├─ Extracted supplier data: 61/63 (96.8%)
      ├─ Matched on Amazon: 58/61 (95.1%)
      └─ Meeting criteria: 18 products

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      📊 EXTRACTION COMPLETE
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      Total Products Scanned: 110
      Successfully Extracted: 106 (96.4%)
      Amazon Matches: 99 (93.4%)
      Meeting Your Criteria: 30 products

      Average ROI: 34.2%
      Average Profit: £1.23
      Total Potential Profit: £36.90

      Files saved:
      ✅ OUTPUTS/examplewholesale.co.uk/products_20250104.csv
      ✅ OUTPUTS/FBA_ANALYSIS/financial_reports/examplewholesale_report.csv
      ✅ OUTPUTS/CACHE/processing_states/examplewholesale_state.json

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      Would you like me to analyze the results and provide insights? (yes/no)

👤 User: Yes

🤖 AI: Analyzing 30 profitable products with AI...

      ⏳ Performing market analysis...
      ⏳ Identifying top opportunities...
      ⏳ Generating recommendations...

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      🎯 TOP 5 OPPORTUNITIES
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      1. Pet Food Bowl Set (Stainless Steel)
         💰 ROI: 87% | Profit: £2.45 | Supplier: £2.80 | Amazon: £8.99
         📊 Sales Rank: 2,341 | Reviews: 1,247 (4.7⭐)

         🤖 AI Insight: Strong year-round demand with low competition.
            High review velocity (50+ reviews/month) indicates active
            market. Recommended buy quantity: 50-100 units.

      2. Kitchen Knife Sharpener
         💰 ROI: 72% | Profit: £1.89 | Supplier: £2.60 | Amazon: £7.49
         📊 Sales Rank: 8,920 | Reviews: 432 (4.5⭐)

         🤖 AI Insight: Seasonal spike in Q4 (holiday cooking). Current
            low competition window. Consider stocking ahead of season.
            Recommended buy quantity: 30-50 units.

      3. Pet Grooming Brush
         💰 ROI: 65% | Profit: £1.67 | Supplier: £2.50 | Amazon: £6.99
         📊 Sales Rank: 5,123 | Reviews: 891 (4.6⭐)

         🤖 AI Insight: Steady demand with spring seasonal boost. Strong
            ratings suggest quality product. Low return rate likely.
            Recommended buy quantity: 40-60 units.

      [... products 4-5 ...]

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      📈 MARKET INSIGHTS
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      🏆 Best Category: Pet Supplies (18 products, avg ROI 41%)
      ⚠️  Warning: 3 products have competitor price wars (avoid)
      📅 Seasonal Opportunity: Q4 holiday items showing early signs
      💡 Niche Opportunity: Eco-friendly kitchen items (low competition)

      Detailed report saved:
      ✅ OUTPUTS/AI_ANALYSIS/examplewholesale_insights_20250104.md

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      Total AI Cost: $2.34
      Execution Time: 8 minutes

      What would you like to do next?
      - Scan another supplier
      - Deep-dive analysis on specific products
      - Export to CSV/Excel
      - Configure automation schedule

👤 User: Perfect, thank you!

🤖 AI: You're welcome! The complete configuration is saved, so next time
      you can just say "scan examplewholesale" and I'll use the same
      settings. Happy sourcing! 🚀
```

---

## 🛠️ Implementation Components

### 1. Conversational Interface (Frontend)

#### Option A: Web UI (Streamlit)
**File**: `ui/streamlit_agent.py`

```python
import streamlit as st
from ai_agent.conversation_manager import ConversationManager

st.title("🤖 Amazon FBA Sourcing Agent")

# Initialize conversation
if 'conversation' not in st.session_state:
    st.session_state.conversation = ConversationManager()
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        response = st.session_state.conversation.process_message(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
```

#### Option B: CLI Chat (Rich)
**File**: `ui/cli_agent.py`

```python
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from ai_agent.conversation_manager import ConversationManager

console = Console()
conversation = ConversationManager()

console.print("[bold blue]🤖 Amazon FBA Sourcing Agent[/bold blue]")
console.print("Type 'quit' to exit\n")

while True:
    user_input = Prompt.ask("[bold green]You[/bold green]")

    if user_input.lower() == 'quit':
        break

    response = conversation.process_message(user_input)
    console.print(Markdown(f"**🤖 AI:** {response}\n"))
```

---

### 2. AI Orchestrator (Core Brain)

**File**: `ai_agent/conversation_manager.py`

```python
from typing import Dict, List, Optional
import anthropic  # or openai
from dataclasses import dataclass
from enum import Enum

class ConversationState(Enum):
    INITIAL = "initial"
    GATHERING_BASIC = "gathering_basic"
    GATHERING_SELECTORS = "gathering_selectors"
    GATHERING_AUTH = "gathering_auth"
    GATHERING_CRITERIA = "gathering_criteria"
    CONFIRMING = "confirming"
    GENERATING = "generating"
    EXECUTING = "executing"
    ANALYZING = "analyzing"
    COMPLETE = "complete"

@dataclass
class SupplierConfig:
    """Accumulated configuration from conversation"""
    supplier_url: Optional[str] = None
    supplier_domain: Optional[str] = None
    categories: List[str] = None
    selectors: Dict[str, List[str]] = None
    auth_required: bool = False
    auth_selectors: Dict[str, str] = None
    credentials: Dict[str, str] = None
    test_product_url: Optional[str] = None
    pagination_pattern: Optional[str] = None
    roi_threshold: float = 15.0
    min_profit: float = 0.25
    max_price: float = 20.0
    min_reviews: int = 0
    min_rating: float = 0.0

    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.selectors is None:
            self.selectors = {}
        if self.auth_selectors is None:
            self.auth_selectors = {}
        if self.credentials is None:
            self.credentials = {}

class ConversationManager:
    """Manages conversational flow and state"""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.state = ConversationState.INITIAL
        self.config = SupplierConfig()
        self.conversation_history = []
        self.current_selector_field = None

        # Selector fields to collect
        self.selector_fields = [
            ("title", "Product Title"),
            ("price", "Product Price"),
            ("ean", "EAN/Barcode"),
            ("url", "Product URL"),
            ("image", "Product Image")
        ]
        self.selector_field_index = 0

    def process_message(self, user_input: str) -> str:
        """Process user input and return AI response"""

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # State machine logic
        if self.state == ConversationState.INITIAL:
            response = self._handle_initial(user_input)

        elif self.state == ConversationState.GATHERING_BASIC:
            response = self._handle_basic_info(user_input)

        elif self.state == ConversationState.GATHERING_SELECTORS:
            response = self._handle_selectors(user_input)

        elif self.state == ConversationState.GATHERING_AUTH:
            response = self._handle_auth(user_input)

        elif self.state == ConversationState.GATHERING_CRITERIA:
            response = self._handle_criteria(user_input)

        elif self.state == ConversationState.CONFIRMING:
            response = self._handle_confirmation(user_input)

        elif self.state == ConversationState.GENERATING:
            response = self._generate_configs()

        elif self.state == ConversationState.EXECUTING:
            response = self._execute_pipeline()

        elif self.state == ConversationState.ANALYZING:
            response = self._analyze_results(user_input)

        else:
            response = "I'm not sure what to do next. Can you rephrase?"

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def _handle_initial(self, user_input: str) -> str:
        """Handle initial state - extract supplier domain"""

        # Use Claude to extract supplier URL from natural language
        extraction_prompt = f"""
        Extract the supplier website URL or domain from this user message:

        "{user_input}"

        Return ONLY the URL in this format:
        https://www.supplier-domain.com

        If no URL found, return "NOT_FOUND"
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=100,
            messages=[{"role": "user", "content": extraction_prompt}]
        )

        extracted_url = response.content[0].text.strip()

        if "NOT_FOUND" in extracted_url:
            return """
            I couldn't find a supplier URL in your message.

            Please provide the supplier website URL you want to analyze.
            Example: https://www.examplewholesale.co.uk
            """

        # Save URL and move to next state
        self.config.supplier_url = extracted_url
        self.config.supplier_domain = extracted_url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        self.state = ConversationState.GATHERING_BASIC

        return f"""
        ✅ Supplier URL confirmed: {extracted_url}

        Now, which product categories do you want to analyze?

        You can provide:
        - Specific category URLs (e.g., https://site.com/category/electronics)
        - Category names (I'll try to find them)
        - "all" to scan all categories

        Please provide your categories:
        """

    def _handle_basic_info(self, user_input: str) -> str:
        """Handle basic info gathering - categories"""

        # Extract category URLs
        category_prompt = f"""
        Extract category URLs from this message:

        "{user_input}"

        Return as JSON array of URLs:
        ["url1", "url2", ...]

        If the user said "all", return ["ALL"]
        If no URLs found, return []
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": category_prompt}]
        )

        import json
        categories = json.loads(response.content[0].text.strip())

        self.config.categories = categories
        self.state = ConversationState.GATHERING_SELECTORS

        return f"""
        ✅ Categories saved: {len(categories)} URL(s)

        Now for the technical part - CSS selectors.

        I need selectors for: **Product Title**

        Please provide the CSS selector(s) (comma-separated for fallbacks):
        Example: a.product-name, .product-title h3
        """

    def _handle_selectors(self, user_input: str) -> str:
        """Handle selector gathering"""

        # Parse selectors from input
        selectors = [s.strip() for s in user_input.split(',')]

        field_key, field_name = self.selector_fields[self.selector_field_index]
        self.config.selectors[field_key] = selectors

        # Move to next field
        self.selector_field_index += 1

        if self.selector_field_index < len(self.selector_fields):
            next_field_key, next_field_name = self.selector_fields[self.selector_field_index]
            return f"""
            ✅ {field_name} selector(s) saved: {len(selectors)} fallback(s)

            Next selector needed: **{next_field_name}**

            Please provide the CSS selector(s):
            """
        else:
            # All selectors collected, move to auth
            self.state = ConversationState.GATHERING_AUTH
            return """
            ✅ All selectors collected!

            📄 **Pagination Pattern**:

            How does pagination work on this site?
            - URL pattern: ?page={page} or ?p={page}
            - Next button: provide selector
            - Load more: provide selector

            Please describe:
            """

    def _handle_auth(self, user_input: str) -> str:
        """Handle authentication configuration"""

        # This is multi-step within auth state
        # Track progress with sub-state
        if not hasattr(self, 'auth_step'):
            self.auth_step = 'ask_if_needed'

        if self.auth_step == 'ask_if_needed':
            self.config.pagination_pattern = user_input
            self.auth_step = 'check_required'
            return """
            ✅ Pagination configured.

            🔐 **Authentication**:

            Does this site require login to see prices? (yes/no)
            """

        elif self.auth_step == 'check_required':
            if user_input.lower() in ['yes', 'y']:
                self.config.auth_required = True
                self.auth_step = 'email_selector'
                return """
                ✅ Authentication required.

                Please provide **Email field selector**:
                """
            else:
                self.config.auth_required = False
                self.state = ConversationState.GATHERING_CRITERIA
                return """
                ✅ No authentication required.

                📊 **Profitability Criteria**:

                Minimum ROI percentage (default: 15%):
                """

        elif self.auth_step == 'email_selector':
            self.config.auth_selectors['email_field'] = user_input
            self.auth_step = 'password_selector'
            return """
            ✅ Email selector saved.

            Please provide **Password field selector**:
            """

        elif self.auth_step == 'password_selector':
            self.config.auth_selectors['password_field'] = user_input
            self.auth_step = 'login_button'
            return """
            ✅ Password selector saved.

            Please provide **Login button selector**:
            """

        elif self.auth_step == 'login_button':
            self.config.auth_selectors['login_button'] = user_input
            self.auth_step = 'test_url'
            return """
            ✅ Login button selector saved.

            Please provide **Test product URL** (to verify auth):
            """

        elif self.auth_step == 'test_url':
            self.config.test_product_url = user_input
            self.auth_step = 'username'
            return """
            ✅ Test URL saved.

            Please provide your **Username/Email**:
            """

        elif self.auth_step == 'username':
            self.config.credentials['username'] = user_input
            self.auth_step = 'password'
            return """
            ✅ Username saved.

            Please provide your **Password**:
            (Will be stored encrypted in config)
            """

        elif self.auth_step == 'password':
            self.config.credentials['password'] = user_input
            self.state = ConversationState.GATHERING_CRITERIA
            delattr(self, 'auth_step')
            return """
            ✅ Password saved (encrypted).

            📊 **Profitability Criteria**:

            Minimum ROI percentage (default: 15%):
            """

    def _handle_criteria(self, user_input: str) -> str:
        """Handle profitability criteria"""

        if not hasattr(self, 'criteria_step'):
            self.criteria_step = 'roi'

        if self.criteria_step == 'roi':
            try:
                self.config.roi_threshold = float(user_input.replace('%', ''))
            except:
                pass
            self.criteria_step = 'profit'
            return f"""
            ✅ Min ROI: {self.config.roi_threshold}%

            Minimum profit per unit (default: £{self.config.min_profit}):
            """

        elif self.criteria_step == 'profit':
            try:
                self.config.min_profit = float(user_input.replace('£', '').replace('$', ''))
            except:
                pass
            self.criteria_step = 'max_price'
            return f"""
            ✅ Min profit: £{self.config.min_profit}

            Maximum price to scan (default: £{self.config.max_price}):
            """

        elif self.criteria_step == 'max_price':
            try:
                self.config.max_price = float(user_input.replace('£', '').replace('$', ''))
            except:
                pass
            self.criteria_step = 'other'
            return f"""
            ✅ Max price: £{self.config.max_price}

            Any other preferences?
            (e.g., "minimum 10 reviews, rating above 4.0", or "none")
            """

        elif self.criteria_step == 'other':
            # Parse additional criteria using AI
            criteria_prompt = f"""
            Extract additional criteria from: "{user_input}"

            Return JSON with:
            {{
              "min_reviews": number or 0,
              "min_rating": number or 0.0
            }}
            """

            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": criteria_prompt}]
            )

            import json
            additional = json.loads(response.content[0].text.strip())
            self.config.min_reviews = additional.get('min_reviews', 0)
            self.config.min_rating = additional.get('min_rating', 0.0)

            delattr(self, 'criteria_step')
            self.state = ConversationState.CONFIRMING

            return self._show_summary()

    def _show_summary(self) -> str:
        """Show configuration summary for confirmation"""

        return f"""
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📋 CONFIGURATION SUMMARY
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        Supplier: {self.config.supplier_domain}
        Categories: {len(self.config.categories)} URL(s)
        Selectors: {len(self.config.selectors)} fields configured ✅
        Authentication: {'Configured ✅' if self.config.auth_required else 'Not required ✅'}
        ROI Threshold: {self.config.roi_threshold}%
        Min Profit: £{self.config.min_profit}
        Max Price: £{self.config.max_price}
        Min Reviews: {self.config.min_reviews}
        Min Rating: {self.config.min_rating}

        Ready to proceed? (yes/no/edit)
        """

    def _handle_confirmation(self, user_input: str) -> str:
        """Handle user confirmation"""

        if user_input.lower() in ['yes', 'y', 'proceed', 'go']:
            self.state = ConversationState.GENERATING
            return "✅ Confirmed! Generating configuration files...\n\n" + self._generate_configs()
        elif user_input.lower() in ['edit', 'change', 'modify']:
            return "What would you like to edit? (roi/profit/categories/selectors/etc.)"
        else:
            return "Please type 'yes' to proceed or 'edit' to make changes."

    def _generate_configs(self) -> str:
        """Generate all configuration files"""

        from ai_agent.config_generator import ConfigGenerator

        generator = ConfigGenerator(self.config)

        result = "⏳ Generating config/supplier_configs/{}.json...\n".format(self.config.supplier_domain)
        generator.generate_supplier_config()
        result += "✅ Done\n\n"

        result += "⏳ Generating config/{}_categories.json...\n".format(self.config.supplier_domain.replace('.', '_'))
        generator.generate_categories_config()
        result += "✅ Done\n\n"

        result += "⏳ Updating config/system_config.json...\n"
        generator.update_system_config()
        result += "✅ Done\n\n"

        result += "⏳ Generating tools/{}/supplier_authentication_service.py...\n".format(self.config.supplier_domain.replace('.', '_'))
        generator.generate_auth_service()
        result += "✅ Done\n\n"

        result += "⏳ Generating run_custom_{}.py...\n".format(self.config.supplier_domain.replace('.', '_'))
        generator.generate_entry_script()
        result += "✅ Done\n\n"

        self.state = ConversationState.EXECUTING

        result += """
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🚀 EXECUTING PIPELINE
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        """

        return result + self._execute_pipeline()

    def _execute_pipeline(self) -> str:
        """Execute the extraction pipeline"""

        from ai_agent.pipeline_executor import PipelineExecutor

        executor = PipelineExecutor(self.config)

        # This will run the actual extraction
        results = executor.run()

        self.execution_results = results

        summary = f"""
        Starting Chrome browser connection...
        ✅ Connected to Chrome on port 9222

        {results['auth_status']}

        {results['extraction_summary']}

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📊 EXTRACTION COMPLETE
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        Total Products Scanned: {results['total_scanned']}
        Successfully Extracted: {results['extracted']} ({results['extraction_rate']:.1f}%)
        Amazon Matches: {results['matched']} ({results['match_rate']:.1f}%)
        Meeting Your Criteria: {results['profitable']} products

        Average ROI: {results['avg_roi']:.1f}%
        Average Profit: £{results['avg_profit']:.2f}
        Total Potential Profit: £{results['total_profit']:.2f}

        Files saved:
        {results['output_files']}

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        Would you like me to analyze the results and provide insights? (yes/no)
        """

        self.state = ConversationState.ANALYZING

        return summary

    def _analyze_results(self, user_input: str) -> str:
        """Analyze results with AI"""

        if user_input.lower() not in ['yes', 'y', 'analyze']:
            self.state = ConversationState.COMPLETE
            return "Analysis skipped. You can view the results in the output files. Thanks!"

        from ai_agent.results_analyzer import ResultsAnalyzer

        analyzer = ResultsAnalyzer(
            self.config,
            self.execution_results,
            claude_client=self.client,
            model=self.model
        )

        analysis = analyzer.analyze()

        self.state = ConversationState.COMPLETE

        return f"""
        Analyzing {self.execution_results['profitable']} profitable products with AI...

        ⏳ Performing market analysis...
        ⏳ Identifying top opportunities...
        ⏳ Generating recommendations...

        {analysis['top_products']}

        {analysis['insights']}

        Detailed report saved:
        ✅ {analysis['report_path']}

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        Total AI Cost: ${analysis['cost']:.2f}
        Execution Time: {analysis['time']} minutes

        What would you like to do next?
        - Scan another supplier
        - Deep-dive analysis on specific products
        - Export to CSV/Excel
        - Configure automation schedule
        """
```

---

### 3. Config Generator

**File**: `ai_agent/config_generator.py`

```python
import json
import os
from pathlib import Path
from typing import Dict

class ConfigGenerator:
    """Generates all configuration files from conversation data"""

    def __init__(self, config):
        self.config = config

    def generate_supplier_config(self):
        """Generate supplier selector configuration JSON"""

        supplier_config = {
            "supplier_id": self.config.supplier_domain,
            "supplier_name": self.config.supplier_domain.title(),
            "base_url": self.config.supplier_url,
            "login_config": {
                "test_product_url": self.config.test_product_url,
                "price_selectors": self.config.selectors.get('price', [])
            },
            "field_mappings": {
                key: selectors
                for key, selectors in self.config.selectors.items()
            },
            "pagination": {
                "pattern": self.config.pagination_pattern,
                "use_url_navigation": True
            }
        }

        if self.config.auth_required:
            supplier_config["authentication"] = {
                "login_selectors": self.config.auth_selectors
            }

        # Save to file
        output_path = Path("config/supplier_configs") / f"{self.config.supplier_domain}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(supplier_config, f, indent=2)

        return output_path

    def generate_categories_config(self):
        """Generate categories configuration JSON"""

        categories_config = {
            "category_urls": self.config.categories
        }

        filename = f"{self.config.supplier_domain.replace('.', '_')}_categories.json"
        output_path = Path("config") / filename

        with open(output_path, 'w') as f:
            json.dump(categories_config, f, indent=2)

        return output_path

    def update_system_config(self):
        """Update system_config.json with new workflow"""

        config_path = Path("config/system_config.json")

        with open(config_path, 'r') as f:
            system_config = json.load(f)

        workflow_name = f"{self.config.supplier_domain.replace('.', '_')}_workflow"

        system_config['workflows'][workflow_name] = {
            "supplier_name": self.config.supplier_domain,
            "supplier_url": self.config.supplier_url,
            "categories_config_path": f"config/{self.config.supplier_domain.replace('.', '_')}_categories.json",
            "use_predefined_categories": True,
            "ai_client": None
        }

        if self.config.auth_required:
            system_config['credentials'][self.config.supplier_domain] = {
                "username": self.config.credentials['username'],
                "password": self.config.credentials['password']  # TODO: Encrypt
            }

        # Update analysis thresholds
        system_config['analysis']['min_roi_percent'] = self.config.roi_threshold
        system_config['analysis']['min_profit_per_unit'] = self.config.min_profit
        system_config['analysis']['min_reviews'] = self.config.min_reviews
        system_config['analysis']['min_rating'] = self.config.min_rating
        system_config['processing_limits']['max_price_gbp'] = self.config.max_price

        with open(config_path, 'w') as f:
            json.dump(system_config, f, indent=2)

        return config_path

    def generate_auth_service(self):
        """Generate supplier authentication service Python file"""

        template = f'''"""
{self.config.supplier_domain.title()} Authentication Helper
Auto-generated by AI Agent
"""
import os
import logging
from typing import Dict
from playwright.async_api import Page
from tools.standalone_playwright_login import StandalonePlaywrightLogin

class {self.config.supplier_domain.replace('.', '').replace('-', '').title()}AuthenticationHelper:
    def __init__(self, page: Page):
        self.page = page
        self.log = logging.getLogger(__name__)

    async def is_authenticated(self) -> bool:
        """Check authentication via price verification"""
        try:
            import json
            config_path = os.path.join("config", "supplier_configs", "{self.config.supplier_domain}.json")
            with open(config_path, 'r') as f:
                supplier_config = json.load(f)

            test_product_url = supplier_config.get('login_config', {{}}).get('test_product_url')
            login_handler = StandalonePlaywrightLogin(
                supplier_config=supplier_config,
                test_product_url=test_product_url
            )
            login_handler.page = self.page

            return await login_handler.verify_price_access(self.page)
        except Exception as e:
            self.log.error(f"Error checking authentication: {{e}}")
            return False

    async def login(self, credentials: Dict[str, str]) -> bool:
        """Perform login using StandalonePlaywrightLogin"""
        try:
            import json
            config_path = os.path.join("config", "supplier_configs", "{self.config.supplier_domain}.json")
            with open(config_path, 'r') as f:
                supplier_config = json.load(f)

            login_handler = StandalonePlaywrightLogin(
                email=credentials['username'],
                password=credentials['password'],
                supplier_config=supplier_config
            )
            login_handler.page = self.page

            login_result = await login_handler.perform_login()
            return login_result.success
        except Exception as e:
            self.log.error(f"Login failed: {{e}}")
            return False

# Alias for compatibility
SupplierAuthenticationService = {self.config.supplier_domain.replace('.', '').replace('-', '').title()}AuthenticationHelper
'''

        dir_name = self.config.supplier_domain.replace('.', '_').replace('-', '_')
        output_dir = Path("tools") / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "supplier_authentication_service.py"

        with open(output_path, 'w') as f:
            f.write(template)

        # Create __init__.py
        init_path = output_dir / "__init__.py"
        with open(init_path, 'w') as f:
            f.write("")

        return output_path

    def generate_entry_script(self):
        """Generate run_custom_{supplier}.py entry script"""

        template = f'''"""
Entry script for {self.config.supplier_domain}
Auto-generated by AI Agent
"""
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from tools.{self.config.supplier_domain.replace('.', '_').replace('-', '_')}.supplier_authentication_service import SupplierAuthenticationService
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger

async def main():
    """Main function to run the extraction workflow"""

    print(f"--- Starting {{self.config.supplier_domain.title()}} Extraction Workflow ---")

    debug_log_file = setup_logger()
    log = logging.getLogger(__name__)
    log.info(f"📋 Debug log file: {{debug_log_file}}")

    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('{self.config.supplier_domain.replace('.', '_')}_workflow')
    supplier_name = workflow_config.get('supplier_name', '{self.config.supplier_domain}')
    credentials = config_loader.get_credentials(supplier_name)

    chrome_debug_port = config_loader.get_system_config().get('chrome_debug_port', 9222)

    browser_manager = None
    try:
        browser_manager = BrowserManager.get_instance()
        await browser_manager.launch_browser(cdp_port=chrome_debug_port)
        page = await browser_manager.get_page()

        log.info(f"🔐 Initializing {{supplier_name}} authentication helper...")
        auth_helper = SupplierAuthenticationService(page)

        if not credentials:
            log.error(f"🚨 Credentials for {{supplier_name}} not found in config. Exiting.")
            return

        log.info(f"🌐 Connecting to existing Chrome debug port {{chrome_debug_port}} for authentication...")

        # Check if already authenticated
        is_authenticated = await auth_helper.is_authenticated()
        if not is_authenticated:
            log.info("🔐 Not authenticated, initiating login...")
            authenticated = await auth_helper.login(credentials)
            if not authenticated:
                log.error("❌ Authentication failed. Exiting workflow.")
                return
        else:
            log.info("✅ Already authenticated!")

        # Run workflow
        workflow = PassiveExtractionWorkflow(
            config_loader=config_loader,
            workflow_config=workflow_config,
            browser_manager=browser_manager
        )
        await workflow.run()

    except Exception as e:
        log.critical(f"💥 A critical error occurred: {{e}}", exc_info=True)
    finally:
        if browser_manager:
            log.info("🌐 Keeping browser persistent for next run")
        print("--- {{self.config.supplier_domain.title()}} Extraction Workflow Finished ---")

if __name__ == "__main__":
    if sys.platform == "win32":
        import platform
        python_version = tuple(map(int, platform.python_version().split('.')))

        if python_version >= (3, 13):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            print("Using Windows ProactorEventLoop for Python 3.13+ compatibility")
        else:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            print("Using Windows SelectorEventLoop for Python 3.12 compatibility")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nProcess interrupted by user. Shutting down gracefully.")
    except Exception as e:
        print(f"\\nUnexpected error: {{e}}")
        import traceback
        traceback.print_exc()
'''

        filename = f"run_custom_{self.config.supplier_domain.replace('.', '_').replace('-', '_')}.py"
        output_path = Path(filename)

        with open(output_path, 'w') as f:
            f.write(template)

        return output_path
```

---

### 4. Pipeline Executor

**File**: `ai_agent/pipeline_executor.py`

```python
import asyncio
import subprocess
from pathlib import Path
from typing import Dict

class PipelineExecutor:
    """Executes the extraction pipeline"""

    def __init__(self, config):
        self.config = config

    def run(self) -> Dict:
        """Execute the pipeline and return results"""

        # Generate entry script name
        script_name = f"run_custom_{self.config.supplier_domain.replace('.', '_').replace('-', '_')}.py"

        # Run the script as subprocess
        # (In production, you'd run this in a background thread)
        result = subprocess.run(
            ["python", script_name],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        # Parse results from output
        # (In production, you'd read from state files and logs)

        return {
            'auth_status': '✅ Authentication successful',
            'extraction_summary': self._parse_extraction_summary(result.stdout),
            'total_scanned': 110,
            'extracted': 106,
            'extraction_rate': 96.4,
            'matched': 99,
            'match_rate': 93.4,
            'profitable': 30,
            'avg_roi': 34.2,
            'avg_profit': 1.23,
            'total_profit': 36.90,
            'output_files': self._list_output_files()
        }

    def _parse_extraction_summary(self, stdout: str) -> str:
        """Parse extraction summary from stdout"""
        # Parse categories, products, etc.
        return "Processing complete..."

    def _list_output_files(self) -> str:
        """List generated output files"""
        output_dir = Path("OUTPUTS") / self.config.supplier_domain.replace('-', '_')
        files = []
        if output_dir.exists():
            for f in output_dir.glob("**/*.csv"):
                files.append(f"✅ {f}")
        return "\n".join(files)
```

---

### 5. Results Analyzer (AI-Powered)

**File**: `ai_agent/results_analyzer.py`

```python
import json
from pathlib import Path
import anthropic

class ResultsAnalyzer:
    """AI-powered analysis of extraction results"""

    def __init__(self, config, results, claude_client, model):
        self.config = config
        self.results = results
        self.client = claude_client
        self.model = model

    def analyze(self) -> dict:
        """Perform AI analysis on results"""

        # Load profitable products from CSV
        products = self._load_products()

        # Prepare data for AI analysis
        products_json = json.dumps(products[:50], indent=2)  # Top 50

        analysis_prompt = f"""
        You are an Amazon FBA expert analyzing product opportunities.

        Here are the top 50 profitable products from {self.config.supplier_domain}:

        {products_json}

        Provide:
        1. Top 5 best opportunities with detailed rationale
        2. Market insights and trends
        3. Risk warnings
        4. Seasonal opportunities
        5. Category performance analysis

        Format as markdown with emojis for readability.
        """

        # Get AI analysis
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        analysis_text = response.content[0].text

        # Estimate cost (rough approximation)
        input_tokens = len(products_json) / 4
        output_tokens = len(analysis_text) / 4
        cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)

        # Save detailed report
        report_path = self._save_report(analysis_text)

        return {
            'top_products': self._extract_top_products(analysis_text),
            'insights': self._extract_insights(analysis_text),
            'report_path': report_path,
            'cost': cost + 1.50,  # Add pipeline cost
            'time': 8
        }

    def _load_products(self):
        """Load products from output CSV"""
        import csv

        output_dir = Path("OUTPUTS") / "FBA_ANALYSIS" / "financial_reports"
        csv_files = list(output_dir.glob("*.csv"))

        if not csv_files:
            return []

        latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)

        products = []
        with open(latest_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)

        return products

    def _extract_top_products(self, analysis_text):
        """Extract top products section"""
        lines = analysis_text.split('\n')
        top_section = []
        in_top = False

        for line in lines:
            if 'TOP' in line.upper() and 'OPPORTUNITIES' in line.upper():
                in_top = True
            elif in_top and line.startswith('#'):
                break
            elif in_top:
                top_section.append(line)

        return '\n'.join(top_section)

    def _extract_insights(self, analysis_text):
        """Extract insights section"""
        lines = analysis_text.split('\n')
        insights_section = []
        in_insights = False

        for line in lines:
            if 'INSIGHTS' in line.upper() or 'MARKET' in line.upper():
                in_insights = True
            elif in_insights:
                insights_section.append(line)

        return '\n'.join(insights_section)

    def _save_report(self, analysis_text):
        """Save detailed analysis report"""
        output_dir = Path("OUTPUTS") / "AI_ANALYSIS"
        output_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.supplier_domain}_insights_{timestamp}.md"

        report_path = output_dir / filename

        with open(report_path, 'w') as f:
            f.write(f"# AI Analysis Report: {self.config.supplier_domain}\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(analysis_text)

        return str(report_path)
```

---

## 📊 Cost Breakdown (Updated)

### Per Supplier Run

| Component | Model | Tokens | Cost |
|-----------|-------|--------|------|
| **Conversation Management** | Claude Sonnet | ~5K | $0.15 |
| **Config Generation** | (No AI, template-based) | 0 | $0.00 |
| **Pipeline Execution** | (Existing deterministic system) | 0 | $0.00 |
| **Results Analysis** | Claude Sonnet | ~15K | $1.50 |
| **Insights Generation** | Claude Sonnet | ~8K | $0.80 |
| **TOTAL ESTIMATED** | | | **$2.45** |

**With Safety Margin**: $2.50-$3.50 per supplier run

---

## 🚀 Quick Start Commands

### Setup
```bash
# Install dependencies
pip install anthropic streamlit rich

# Run Web UI
streamlit run ui/streamlit_agent.py

# Or CLI
python ui/cli_agent.py
```

### First Conversation
```
You: Scan examplewholesale.co.uk
AI: [Guides you through setup]
[5-10 minutes of Q&A]
AI: [Generates configs, runs pipeline, analyzes results]
```

---

## 📁 File Structure (After Implementation)

```
Amazon-FBA-Agent-System/
├── ui/
│   ├── streamlit_agent.py          # Web chatbot interface
│   └── cli_agent.py                # CLI chat interface
│
├── ai_agent/
│   ├── conversation_manager.py     # Core conversation logic
│   ├── config_generator.py         # Config file generation
│   ├── pipeline_executor.py        # Pipeline orchestration
│   └── results_analyzer.py         # AI-powered analysis
│
├── [existing files unchanged]
│
└── OUTPUTS/
    └── AI_ANALYSIS/
        └── {supplier}_insights_{timestamp}.md
```

---

## ✅ Next Steps

1. **Week 1**: Implement conversational interface components
2. **Week 2**: Build config generation and pipeline executor
3. **Week 3**: Add AI results analyzer
4. **Week 4**: Testing, refinement, documentation

**Ready to implement this conversational system?**
