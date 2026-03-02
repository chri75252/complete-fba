Task 6 Test Attempt - 2026-02-26:

**Issue:** Playwright automation cannot properly interact with Streamlit chat input
- Dashboard starts on port 8501
- Chat tab is accessible but message input goes to wrong field
- Message appears in "Base Directory" field instead of chat input
- No job created in OUTPUTS/CONTROL_PLANE/jobs/pending/

**Root cause:** Streamlit's chat_input widget has complex DOM structure that Playwright cannot reliably target. The first text input on the page is the "Base Directory" field in the sidebar, not the chat input.

**Next steps:** 
- Need manual testing or different automation approach
- May need to fix chat input selector or UI layout
