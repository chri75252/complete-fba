# Local LLM Integration with Serena MCP: Implementation Guide

**Version**: 1.0  
**Date**: 2026-01-29  
**Status**: Implementation Guidance  

---

## Executive Summary

This document explains how to integrate a locally running LLM (e.g., Ollama with Qwen3-8B) with Serena MCP to leverage the generated codebase index (131.9 MB symbol cache covering 1096 Python files).

**Key Recommendation**: Use **Serena MCP's native semantic search tools** rather than building a custom RAG system.

---

## 1. Current State Analysis

### 1.1 Available Infrastructure

| Component | Status | Details |
|-----------|--------|---------|
| **Serena MCP** | ✅ Active | Project activated with Python index |
| **Codebase Index** | ✅ Ready | 1096 files indexed, 131.9 MB cache |
| **Serena Tools** | ✅ Available | `find_symbol`, `find_referencing_symbols`, `get_symbols_overview` |
| **Local LLM** | ⚠️ Configurable | Ollama with Qwen3-8B model |

### 1.2 Index Location

```
.serena/cache/python/
├── raw_document_symbols.pkl (17.96 MB) - Raw LSP data
└── document_symbols.pkl (113.9 MB) - Processed symbol cache
```

### 1.3 Symbol Structure

Index contains for each file:
- Classes, functions, methods
- Symbol names and locations (file path, line numbers)
- Symbol relationships (imports, inheritance, references)
- Metadata for semantic understanding

---

## 2. Two Integration Approaches

### Approach A: Build Custom RAG System ("Read from Index")

**Concept**: Extract and store index data separately, then build a custom retrieval system.

```
┌─────────────────────────────────────────────────────────────┐
│  LSP Index (.pkl) │
│       ↓           │
│  [Custom Python Code]   │
│  - Extract symbols  │
│  - Create embeddings  │
│  - Build vector store  │
│       ↓           │
│  [Vector Database]     │
│  - FAISS/Chroma/Qdrant │
│  - Similarity search   │
│       ↓           │
│  [Query Engine]       │
│  - Semantic search    │
│  - Reranking         │
│       ↓           │
│  Local LLM (Ollama) │
└─────────────────────────────────────────────────────────────┘
```

#### Pros:
- ✅ Full control over retrieval algorithm
- ✅ Can implement custom scoring/ranking
- ✅ Can add metadata filters, weighting
- ✅ No dependency on Serena's tool limitations
- ✅ Can cache embeddings for speed

#### Cons:
- ❌ **Complex**: Requires vector database (FAISS/Chroma/Qdrant)
- ❌ **Heavy**: Needs embedding model for semantic search
- ❌ **Maintenance**: Two systems to maintain (RAG + index updates)
- ❌ **Duplicated Effort**: Serena already indexed symbols; now indexing again
- ❌ **Maintenance Overhead**: Index changes require vector re-embedding
- ❌ **Technical Risk**: Custom RAG may be less accurate than LSP semantic search
- ❌ **Time Investment**: 3-5 days for production-grade system

#### Estimated Implementation Effort:
| Task | Time |
|------|------|
| Extract .pkl to usable format | 2-4 hours |
| Set up vector database | 2-4 hours |
| Integrate with Ollama API | 4-6 hours |
| Implement retrieval + ranking | 6-8 hours |
| Testing and optimization | 4-6 hours |
| **Total** | **18-28 hours** |

---

### Approach B: Use Serena MCP Native Semantic Search ✅ RECOMMENDED

**Concept**: Leverage Serena's existing semantic search tools directly via MCP protocol.

```
┌─────────────────────────────────────────────────────────────┐
│  User Input          │
│       ↓           │
│  [Local LLM + MCP Client] │
│  - natural language query  │
│  - call Serena MCP tools  │
│       ↓           │
│  [Serena MCP Server]  │
│  - find_symbol()        │
│  - find_referencing_symbols() │
│  - get_symbols_overview() │
│       ↓           │
│  [LSP Index (.pkl)] │
│  - Semantic symbol lookup │
│  - Symbol relationships   │
│       ↓           │
│  Results (Code snippets) │
│       ↓           │
│  User + Natural Language Summary │
└─────────────────────────────────────────────────────────────┘
```

#### Pros:
- ✅ **Simple**: No additional infrastructure needed
- ✅ **Fast**: Uses optimized LSP semantic search (already built)
- ✅ **Maintainable**: Serena handles index updates automatically
- ✅ **Accurate**: LSP provides precise symbol understanding
- ✅ **Low Effort**: 2-4 hours integration time
- ✅ **Production-Ready**: Serena tools battle-tested
- ✅ **Semantic**: Understands code structure (inheritance, calls, types)
- ✅ **Context-Aware**: Provides file paths + line numbers
- ✅ **Zero Maintenance**: No vector DB to manage

#### Cons:
- ⚠️ Limited to Serena's tool capabilities (can't extend easily)
- ⚠️ Black-box (can't see retrieval algorithm)
- ⚠️ Requires MCP client that supports tool calling

#### Estimated Implementation Effort:
| Task | Time |
|------|------|
| Configure MCP client for Serena | 1-2 hours |
| Test tool calls | 1-2 hours |
| Implement natural language wrapper | 1-2 hours |
| **Total** | **3-6 hours** |

---

## 3. Detailed Comparison

| Criterion | Approach A (RAG) | Approach B (Serena MCP) |
|-----------|-------------------|----------------------|
| **Implementation Time** | 18-28 hours | 3-6 hours |
| **Infrastructure Complexity** | High (vector DB + embeddings) | Low (MCP only) |
| **Maintenance** | High (two systems) | Low (automatic) |
| **Search Quality** | Depends on embedding quality | High (LSP semantic) |
| **Flexibility** | High (custom algorithms) | Medium (limited by tools) |
| **Speed** | Fast (cached vectors) | Fast (LSP optimized) |
| **Accuracy** | Medium (semantic similarity) | High (precise symbol lookup) |
| **Cost** | High (compute for embeddings) | Low (leveraged infrastructure) |
| **Risk** | Medium (new code) | Low (existing system) |

---

## 4. Recommended Implementation: Approach B (Serena MCP)

### 4.1 Why Approach B is Better

1. **Leverages Existing Investment**
   - Serena has already indexed 1096 files (131.9 MB)
   - Building custom RAG duplicates this effort

2. **LSP Semantic Search > Vector Similarity**
   - LSP understands **code structure** (inheritance, calls, types)
   - Vector search only understands **text similarity**
   - For code navigation, precision > similarity

3. **Qwen3-8B Compatibility**
   - Model supports tool calling + thinking mode
   - Serena exposes tools via MCP protocol
   - PRD confirms this architecture works

4. **Minimal Disruption**
   - No new infrastructure to maintain
   - No duplicate index management
   - Serena handles index updates automatically

5. **Production-Ready**
   - Serena tools are tested and optimized
   - Simpler implementation = fewer bugs

### 4.2 When Approach A Might Be Better

Approach A (Custom RAG) would be preferred **ONLY IF**:
- You need custom ranking algorithms not in Serena
- You want to combine code index with other data sources (docs, traces, logs)
- You need cross-repository semantic search (not code-aware)
- You're building a specialized code search service

**For your use case (code understanding/navigation)**, Approach B is superior.

---

## 5. Implementation Steps (Approach B)

### 5.1 Prerequisites

| Requirement | Status | Command |
|-------------|--------|---------|
| **Ollama Server** | ⚠️ Required | `ollama serve qwen3:8b --port 11434` |
| **MCP Client** | ⚠️ Required | See Section 5.2 |
| **Serena MCP Server** | ✅ Ready | Already activated |
| **Codebase Index** | ✅ Ready | 131.9 MB cached |

### 5.2 Step-by-Step Guide

#### Step 1: Start Ollama Server

```bash
# Download Qwen3:8B model (if not already downloaded)
ollama pull qwen3:8b

# Start Ollama server on port 11434
ollama serve qwen3:8b --port 11434
```

**Verify it's running**:
```bash
curl http://localhost:11434/api/tags
```

Expected output:
```json
{
  "models": [
    {"name": "qwen3:8b", "modified_at": "..."}
  ]
}
```

#### Step 2: Choose MCP Client

You need an MCP client that can:
1. Connect to Serena MCP server
2. Connect to Ollama server
3. Call Serena tools and Ollama in the same request

**Options**:

| Client | Type | Tool Calling | Notes |
|--------|------|---------------|-------|
| **Claude Desktop** | Native | ✅ Built-in MCP support | Recommended |
| **Claude Code** | Native | ✅ Built-in MCP support | Recommended |
| **OpenWebUI** | Web UI | ✅ MCP support | Good for web interface |
| **Jan.ai** | Desktop | ✅ MCP support | Desktop client |
| **Cline** | VSCode extension | ✅ MCP support | IDE-integrated |
| **Custom Python** | Library | ✅ mcp-python-sdk | Build your own |

#### Step 3: Configure Serena MCP

**Option A: Claude Desktop (Easiest)**

Edit Claude Desktop config:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx --from git+https://github.com/oraios/serena serena start-mcp-server --project \"C:\\Users\\chris\\Desktop\\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\" --context desktop-app",
      "env": {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "qwen3:8b"
      }
    }
  }
}
```

**Option B: Custom Python Client**

Create `local_llm_integration.py`:

```python
"""
Custom MCP client integrating Ollama + Serena MCP.
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.types import TextContent

async def main():
    """Main integration loop."""
    # Connect to Serena MCP
    server_params = StdioServerParameters(
        command="uvx --from git+https://github.com/oraios/serena serena start-mcp-server "
               "--project \"C:\\Users\\chris\\Desktop\\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\" "
               "--context desktop-app"
    )
    
    async with ClientSession(server_params) as session:
        # Connect to Ollama (if you want LLM for reasoning)
        ollama_base_url = "http://localhost:11434"
        ollama_model = "qwen3:8b"
        
        print("=== Local LLM + Serena MCP Integration ===\n")
        
        # Interactive loop
        while True:
            # Get user input
            user_query = input("\nYour query: ").strip()
            
            if not user_query or user_query.lower() in ['exit', 'quit']:
                break
            
            # Call Serena tool based on query intent
            if "find" in user_query and ("class" in user_query or "function" in user_query):
                # Use Serena's find_symbol
                print(f"🔍 Searching for symbol: {user_query}")
                result = await session.call_tool("find_symbol", {
                    "name_path_pattern": user_query.split("find")[-1].strip(),
                    "relative_path": "."
                })
                print(f"\nFound: {json.dumps(result, indent=2)}\n")
            
            elif "referenced" in user_query:
                # Use Serena's find_referencing_symbols
                print(f"🔍 Finding references to symbol...")
                result = await session.call_tool("find_referencing_symbols", {
                    "line": 1,
                    "character": 1,
                    "relative_path": "."
                })
                print(f"\nFound: {json.dumps(result, indent=2)}\n")
            
            elif "structure" in user_query or "overview" in user_query:
                # Use Serena's get_symbols_overview
                print(f"📋 Getting file structure...")
                result = await session.call_tool("get_symbols_overview", {
                    "relative_path": tools/passive_extraction_workflow_latest.py
                })
                print(f"\nFound: {json.dumps(result, indent=2)}\n")
            
            else:
                # Fallback: Ask Ollama for natural language explanation
                print(f"💭 Querying Ollama for: {user_query}")
                
                # Call Ollama API directly
                ollama_prompt = f"""
You are helping analyze an Amazon FBA codebase using Serena MCP tools.
                
Context: The user is working on an Amazon FBA scraping system with the following structure:
- Main workflow: tools/passive_extraction_workflow_latest.py
- Configuration: config/system_config.json
- Browser management: utils/browser_manager.py
- Financial calculator: tools/FBA_Financial_calculator.py

The codebase has been indexed by Serena MCP with semantic symbol information covering 1096 Python files.

Available Serena tools:
- find_symbol: Find classes/functions by name
- find_referencing_symbols: Find where symbols are used
- get_symbols_overview: Get structure overview of a file

User query: {user_query}

If the user is asking for code information, use this knowledge to help them navigate the codebase effectively.
Be conversational, clear, and helpful in natural language.
"""
                
                import requests
                response = requests.post(
                    f"{ollama_base_url}/api/generate",
                    json={
                        "model": ollama_model,
                        "prompt": ollama_prompt,
                        "stream": False
                    },
                    timeout=60
                )
                response.raise_for_status()
                ollama_response = response.json().get("response", "")
                
                # Check if response suggests tool use
                if any(tool in ollama_response for tool in ["find_symbol", "find_referencing_symbols"]):
                    print(f"\n🔧 LLM suggests using Serena tool: {tool}\n")
                else:
                    print(f"\n💬 LLM response:\n{ollama_response}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Step 4: Test the Integration

**Test queries to try**:

1. **Symbol search**:
   ```
   find class PassiveExtractionWorkflow
   find function run_calculations
   ```

2. **Reference finding**:
   ```
   show where BrowserManager is used
   find all references to run_custom_poundwholesale
   ```

3. **Structure overview**:
   ```
   show structure of tools/passive_extraction_workflow_latest.py
   ```

4. **Natural language question**:
   ```
   how does the product cache work?
   what is the purpose of the state manager?
   ```

---

## 6. Advanced Configuration

### 6.1 Customizing Serena Tool Responses

Some tools may return large responses. You can customize:

```python
# In custom client, add response processing
async def call_tool_with_truncation(session, tool_name, params):
    """Call Serena tool with result truncation."""
    result = await session.call_tool(tool_name, params)
    
    # Truncate large responses if needed
    if isinstance(result, dict) and len(str(result)) > 10000:
        print(f"\n⚠️ Response truncated (10k chars shown):\n")
        print(str(result)[:10000])
        print(f"\n... [Result truncated. Full result in {tool_name} output]\n")
    else:
        print(json.dumps(result, indent=2))
    
    return result
```

### 6.2 Adding RAG to Serena (Optional Enhancement)

If you want **both** Serena semantic search **AND** semantic similarity across documents:

```python
"""
Enhanced integration combining Serena MCP + custom RAG.
"""
async def hybrid_search(session, user_query, ollama_url):
    """Combine Serena's precise symbol search with broader semantic search."""
    
    # 1. Try Serena first (fast, precise)
    serena_result = await session.call_tool("find_symbol", {
        "name_path_pattern": user_query
    })
    
    if serena_result.get("found"):
        return serena_result
    
    # 2. Fallback to custom RAG
    print("🔄 No symbol found, searching documents...")
    
    # Query your RAG system
    rag_response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": "qwen3:8b",
            "prompt": f"Search for: {user_query}",
            "stream": False
        },
        timeout=60
    ).json()
    
    return {
        "source": "rag",
        "result": rag_response.get("response", "")
    }
```

---

## 7. Troubleshooting

### 7.1 Common Issues

| Issue | Solution |
|-------|----------|
| **Serena MCP not starting** | Check uvx is in PATH, verify project path |
| **Ollama not accessible** | Verify `ollama serve` is running, check firewall |
| **Index outdated** | Re-run: `uvx --from git+https://github.com/oraios/serena serena project index` |
| **Tool calls failing** | Check tool names match Serena's exact API |
| **Slow responses** | Consider caching frequent queries, or smaller model |

### 7.2 Debugging Commands

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check Serena MCP logs
# Located in: .serena/logs/

# Test Serena tool directly
uvx --from git+https://github.com/oraios/serena serena find_symbol --help

# Verify index exists
ls -lh .serena/cache/python/
```

---

## 8. Summary and Recommendation

### 8.1 Decision Matrix

| Factor | Approach A (RAG) | Approach B (Serena MCP) |
|--------|-------------------|----------------------|
| Implementation Time | 18-28 hours | 3-6 hours |
| Maintenance Overhead | High | Low |
| Search Quality | Medium | High |
| Flexibility | High | Medium |
| Infrastructure Needed | Vector DB + Embeddings | MCP Client |
| Recommended For | Specialized services | Code navigation |
| Production Risk | Medium | Low |

### 8.2 Final Recommendation

**Use Approach B (Serena MCP Native Tools)**

**Reasons**:
1. **Leverages your existing investment** (131.9 MB index already built)
2. **Faster implementation** (6x less time)
3. **Higher accuracy** for code understanding (LSP semantic > vector similarity)
4. **Lower maintenance** (automatic index updates vs manual re-embedding)
5. **Production-ready tools** (tested by Serena community)
6. **Simpler architecture** (one integration point vs three systems)

### 8.3 Success Criteria

Your integration is successful when:
- ✅ User can query in natural language
- ✅ LLM uses Serena's semantic tools appropriately
- ✅ Code snippets are returned with context (file paths, line numbers)
- ✅ Responses are clear and actionable
- ✅ System is performant (< 5s for tool calls, < 10s for generation)

---

## 9. Next Steps

1. **Start Ollama server** (if not running):
   ```bash
   ollama serve qwen3:8b --port 11434
   ```

2. **Choose MCP client**:
   - **Quick start**: Use Claude Desktop (Edit config file)
   - **Custom**: Build Python client (see Step 5.2, Option B)

3. **Test integration**:
   - Try the test queries in Section 5.4
   - Verify tool calls are working correctly
   - Check response quality and speed

4. **Optional enhancement**:
   - Add custom RAG on top of Serena if needed for broader semantic search
   - Implement query caching for frequent requests
   - Add conversational context/memory

---

## 10. References

- **Serena Documentation**: https://oraios.github.io/serena/
- **Serena GitHub**: https://github.com/oraios/serena
- **Ollama Documentation**: https://ollama.com/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Qwen Models**: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- **Your PRD**: SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md

---

**End of Document**
