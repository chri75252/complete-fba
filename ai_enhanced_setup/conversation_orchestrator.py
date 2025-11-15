#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversation Orchestrator - Full Implementation with Claude Sonnet 3.5

Natural language interface for supplier configuration using Anthropic Claude.

Features:
- Conversational data collection
- CSS selector guidance
- Budget tracking
- State persistence
- Resume capability

Session 5 Implementation
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Anthropic library not available. Install with: pip install anthropic")

from ai_enhanced_setup.conversation_state_manager import ConversationStateManager

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a helpful AI assistant for Amazon FBA supplier configuration.

Your role:
1. Guide user through supplier setup conversationally
2. Collect required information:
   - Supplier domain (e.g., poundwholesale.co.uk)
   - Categories to scan (names and URLs)
   - CSS selectors for: title, price, EAN, product URL, image
   - Price range (min/max in GBP)
   - Target ROI percentage (default: 25%)
3. Provide guidance on obtaining CSS selectors when needed
4. Confirm all data before finalizing

Important:
- CSS selectors are USER-PROVIDED (guide them, don't guess)
- Ask one question at a time for clarity
- Keep conversation under 10 exchanges to stay within budget
- Be conversational and encouraging
- When user provides selectors, acknowledge and move to next field

DevTools guidance template:
"To find CSS selectors:
1. Open Chrome and navigate to a product page on {domain}
2. Right-click on the element → 'Inspect' (or press F12)
3. In DevTools, right-click the highlighted HTML → 'Copy' → 'Copy selector'
4. Paste it here

Example selectors: .product-title, .price, [data-ean], .product-link"
"""


class ConversationOrchestrator:
    """
    Conversational interface for supplier configuration using Claude Sonnet 3.5.
    """
    
    def __init__(self, anthropic_api_key: Optional[str] = None, budget_limit: float = 0.10):
        """
        Initialize conversation orchestrator.
        
        Args:
            anthropic_api_key: Anthropic API key (or from env ANTHROPIC_API_KEY)
            budget_limit: Conversation budget limit in USD
        """
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("Anthropic library not installed. Install with: pip install anthropic")
        
        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided and not found in environment")
        
        self.client = Anthropic(api_key=api_key)
        self.budget_limit = budget_limit
        self.cost_tracker = 0.0
        self.conversation_history: List[Dict[str, str]] = []
        self.collected_data: Dict[str, Any] = {}
        self.state_manager = ConversationStateManager()
        self.session_id = self.state_manager.generate_session_id()
        
        logger.info(f"ConversationOrchestrator initialized (session: {self.session_id})")
    
    def start_conversation(self, initial_message: Optional[str] = None) -> str:
        """
        Start conversational setup flow.
        
        Args:
            initial_message: Optional initial user message
            
        Returns:
            AI response string
        """
        if initial_message:
            user_msg = initial_message
        else:
            user_msg = "I want to set up a new supplier for my Amazon FBA system."
        
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_msg
        })
        
        # Call Claude
        response_text, cost = self._call_claude()
        
        # Track cost
        self.cost_tracker += cost
        
        # Add assistant response
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        # Save state
        self._save_state()
        
        return response_text
    
    def continue_conversation(self, user_message: str) -> Dict[str, Any]:
        """
        Continue conversation with user input.
        
        Args:
            user_message: User's message
            
        Returns:
            Dict with response, completion status, cost, and collected data
        """
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Check budget before calling
        if self.cost_tracker >= self.budget_limit:
            response = self.handle_budget_exceeded()
            complete = self.check_completion(self.collected_data)
            
            return {
                "response": response,
                "complete": complete,
                "cost_so_far": self.cost_tracker,
                "collected_data": self.collected_data,
                "budget_exceeded": True
            }
        
        # Call Claude
        response_text, cost = self._call_claude()
        
        # Track cost
        self.cost_tracker += cost
        
        # Add assistant response
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        # Extract structured data
        self.collected_data = self.extract_structured_data(self.conversation_history)
        
        # Check completion
        complete = self.check_completion(self.collected_data)
        
        # Save state
        self._save_state(complete=complete)
        
        return {
            "response": response_text,
            "complete": complete,
            "cost_so_far": self.cost_tracker,
            "collected_data": self.collected_data,
            "budget_exceeded": False
        }
    
    def extract_structured_data(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract structured configuration data from conversation.
        
        Returns:
            Partially filled configuration dict
        """
        # Combine all messages for pattern matching
        all_text = "\n".join([msg["content"] for msg in conversation_history])
        
        data: Dict[str, Any] = {}
        
        # Extract domain (pattern: word.co.uk, word.com, etc.)
        domain_match = re.search(r'\b([a-z0-9-]+\.(co\.uk|com|org|net))\b', all_text, re.IGNORECASE)
        if domain_match:
            data["supplier_domain"] = domain_match.group(1).lower()
        
        # Extract categories (look for "Category:" or URL patterns)
        categories = []
        category_pattern = re.compile(r'([A-Z][a-z]+):\s*(https?://[^\s]+)', re.MULTILINE)
        for match in category_pattern.finditer(all_text):
            categories.append({
                "name": match.group(1),
                "url": match.group(2)
            })
        if categories:
            data["categories"] = categories
        
        # Extract selectors (look for CSS selector patterns)
        field_mappings = {}
        selector_patterns = {
            "title": [r'title.*?:\s*([.#\[][\w\-\[\]="]+)', r'Title.*?:\s*([.#\[][\w\-\[\]="]+)'],
            "price": [r'price.*?:\s*([.#\[][\w\-\[\]=".\s]+)', r'Price.*?:\s*([.#\[][\w\-\[\]=".\s]+)'],
            "ean": [r'ean.*?:\s*([.#\[][\w\-\[\]="]+)', r'EAN.*?:\s*([.#\[][\w\-\[\]="]+)', r'barcode.*?:\s*([.#\[][\w\-\[\]="]+)'],
            "url": [r'url.*?:\s*([.#\[][\w\-\[\]="]+)', r'URL.*?:\s*([.#\[][\w\-\[\]="]+)', r'link.*?:\s*([.#\[][\w\-\[\]="]+)'],
            "image": [r'image.*?:\s*([.#\[][\w\-\[\]=".\s]+)', r'Image.*?:\s*([.#\[][\w\-\[\]=".\s]+)']
        }
        
        for field, patterns in selector_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    field_mappings[field] = [match.group(1).strip()]
                    break
        
        if field_mappings:
            data["field_mappings"] = field_mappings
        
        # Extract price range (pattern: £1-20, 1-20, £1 to £20)
        price_range_match = re.search(r'£?(\d+)\s*(?:to|-)\s*£?(\d+)', all_text)
        if price_range_match:
            data["price_range"] = {
                "min": float(price_range_match.group(1)),
                "max": float(price_range_match.group(2))
            }
        
        # Extract ROI (pattern: 25%, ROI 30, etc.)
        roi_match = re.search(r'(?:ROI|roi|target)\s*:?\s*(\d+)%?', all_text)
        if roi_match:
            data["target_roi"] = int(roi_match.group(1))
        
        return data
    
    def check_completion(self, collected_data: Dict[str, Any]) -> bool:
        """
        Check if all required data has been collected.
        
        Args:
            collected_data: Data collected so far
            
        Returns:
            True if complete, False otherwise
        """
        required_fields = [
            "supplier_domain",
            "categories",
            "field_mappings",
            "price_range"
        ]
        
        for field in required_fields:
            if field not in collected_data:
                return False
            
            # Additional checks
            if field == "categories" and len(collected_data[field]) == 0:
                return False
            if field == "field_mappings":
                fm = collected_data[field]
                if not all(k in fm for k in ["title", "price", "ean", "url"]):
                    return False
        
        return True
    
    def generate_confirmation_summary(self, collected_data: Dict[str, Any]) -> str:
        """
        Generate confirmation summary for user review.
        
        Args:
            collected_data: Collected configuration data
            
        Returns:
            Formatted confirmation string
        """
        summary = "📋 Configuration Summary:\n\n"
        
        if "supplier_domain" in collected_data:
            summary += f"• Supplier: {collected_data['supplier_domain']}\n"
        
        if "categories" in collected_data:
            summary += f"• Categories:\n"
            for cat in collected_data['categories']:
                summary += f"  - {cat['name']}: {cat['url']}\n"
        
        if "field_mappings" in collected_data:
            summary += "• Selectors:\n"
            for field, selectors in collected_data['field_mappings'].items():
                summary += f"  - {field}: {selectors[0]}\n"
        
        if "price_range" in collected_data:
            pr = collected_data['price_range']
            summary += f"• Price Range: £{pr['min']}-£{pr['max']}\n"
        
        if "target_roi" in collected_data:
            summary += f"• Target ROI: {collected_data['target_roi']}%\n"
        
        summary += f"\n💰 Cost so far: ${self.cost_tracker:.3f}\n\n"
        summary += "Does this look correct? (yes to proceed, no to make changes)"
        
        return summary
    
    def handle_budget_exceeded(self) -> str:
        """Handle budget exceeded scenario."""
        return ("⚠️ Conversation budget limit ($" + f"{self.budget_limit:.2f}) reached. " +
                "Proceeding with collected information. Please review and confirm data below.")
    
    def load_from_state(self, session_id: str) -> bool:
        """
        Load conversation from saved state.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if loaded successfully
        """
        state = self.state_manager.load_state(session_id)
        
        if not state:
            return False
        
        self.session_id = session_id
        self.conversation_history = state.get("conversation_history", [])
        self.cost_tracker = state.get("cost_tracker", 0.0)
        self.collected_data = state.get("collected_data", {})
        
        logger.info(f"Loaded conversation state from session: {session_id}")
        return True
    
    def _call_claude(self) -> tuple[str, float]:
        """
        Call Claude API with conversation history.
        
        Returns:
            Tuple of (response_text, cost)
        """
        try:
            response = self.client.messages.create(
                model="claude-sonnet-3-5-20241022",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=self.conversation_history
            )
            
            response_text = response.content[0].text
            
            # Calculate cost (Claude Sonnet 3.5 pricing)
            # Input: $0.003 per 1K tokens, Output: $0.015 per 1K tokens
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
            
            logger.debug(f"Claude response: {len(response_text)} chars, cost: ${cost:.4f}")
            
            return response_text, cost
            
        except Exception as e:
            logger.exception(f"Failed to call Claude API: {e}")
            raise RuntimeError(f"Claude API call failed: {e}")
    
    def _save_state(self, complete: bool = False) -> None:
        """Save current conversation state."""
        state = {
            "conversation_history": self.conversation_history,
            "cost_tracker": self.cost_tracker,
            "collected_data": self.collected_data,
            "complete": complete
        }
        
        self.state_manager.save_state(self.session_id, state)


if __name__ == "__main__":
    # Test implementation (requires ANTHROPIC_API_KEY in environment)
    logging.basicConfig(level=logging.INFO)
    
    if not ANTHROPIC_AVAILABLE:
        print("❌ Anthropic library not installed")
        print("   Install with: pip install anthropic")
    elif not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set in environment")
        print("   Set with: export ANTHROPIC_API_KEY='sk-ant-...'")
    else:
        print("✅ Ready to test ConversationOrchestrator")
        print("   Call orchestrator.start_conversation() to begin")
