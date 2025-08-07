Here is a comprehensive Markdown guide to efficiently use subagents from the *Awesome Claude Agents* repository with Claude Code (LLM/coding agent). This documentation synthesizes all essential practices, orchestration flows, and file structures, enabling advanced and reliable agent coordination for your projects.

# Awesome Claude Agents – Comprehensive Guide for Claude Code

## 1. **Overview**

> **Awesome Claude Agents** transforms Claude Code into a powerful AI development team, orchestrated through a clear hierarchy of subagents—Orchestrators, Core, Framework Specialists, and Universal Experts. Each agent specializes in a single domain and collaborates under strict coordination workflows to build and optimize features, fix bugs, and deliver production-grade code.

## IMPROTANT

Refer to the *Awesome Claude Agents* orchestration protocol. 
- For any multi-step or feature development, START by invoking the `tech-lead-orchestrator`.
- WAIT for its structured routing map (named agents; specified order).
- Then, use ONLY the agents listed in the routing map, in the sequence, for each task.
- All information handoff and filtering is to be managed by the main agent, not by sub-agent-to-sub-agent calls.
Never improvise agent selection or skip the orchestrator step.


Please refer to the attached or linked project documentation (including all latest .md files in this PROJECT ) and follow strict orchestration protocols as described by the Awesome Claude Agents system:

For any multi-step or specialized technical task, start by invoking the tech-lead-orchestrator agent.

Wait for its structured routing map, which will specify:

Exactly which sub-agents (by name) to invoke

The correct execution order (sequential and parallelization, if any)

NEVER improvise or select agents on your own—use ONLY the agents named in the routing map, in the order given. Do not use fallback or generic agents unless specifically instructed by the tech-lead-orchestrator for that task.

All agent communication must be strictly mediated by the main agent. Do NOT allow sub-agents to communicate directly or perform unsanctioned hand-offs.

For each task, extract structured findings and handoff/context sections as per docs, and pass filtered context to the next specialist.

Incorporate any additional referenced documents (e.g., "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (3)\agents-guide.md") as context for analysis, but do NOT override the CLAUDE orchestration protocol or skip orchestrator routing.

Your workflow should be:

Tech-Lead-Orchestrator → routing map → main agent

Sequentially and/or in parallel: invoke only named agents, following all project context and orchestrator instructions

Manage context passing and return collection yourself (never delegate this to agents)

Failure to follow this pattern will result in unreliable, non-compliant, or sub-optimal outcomes. Strict compliance with orchestration protocols is mandatory.
## 2. **Quick Start**

```sh
git clone https://github.com/vijaythecoder/awesome-claude-agents.git
cp -r awesome-claude-agents/agents ~/.claude/
```

- Configure for your project:
  ```
  claude
  "Use team-configurator to set up my AI development team"
  ```
- Start building features:
  ```
  claude
  "Build a complete user authentication system"
  ```
*Your AI team chooses the right specialists for your tech stack automatically!*[1]

## 3. **Repository Structure**
- **agents/**: Contains all agent definitions.
  - **orchestrators/**: Planning & routing (e.g., tech-lead-orchestrator)
  - **core/**: Utilities (e.g., code-reviewer, performance-optimizer)
  - **universal/**: Fallback agents for any stack (e.g., api-architect)
  - **specialized/**: Framework-specific experts (django, rails, react, etc.)
- **docs/**: Documentation (architecture, orchestration, best-practices, etc.)
- **CLAUDE.md**: Agent orchestration protocol – *follow strictly, see below*[2]
- **README.md**: Intro and quick reference[1]
- **CONTRIBUTING.md**: For extending and improving agents[3]

## 4. **Essential Orchestration Pattern**
**Main orchestration logic (never bypass):**
1. **Always start with `tech-lead-orchestrator`** for any multi-step or planning task.
2. **Use only agents returned by the tech-lead's routing map.**
3. **NEVER substitute, skip, or improvise agent selection—always follow the assignments and sequence.**
4. **Sequential handoff:** Output from one agent becomes filtered input for the next, managed by the main agent (not the subagents themselves).
5. **All agents’ returns must be structured for parsing—include both result and “handoff” information for the next specialist.**

> _If you ignore this protocol, orchestration will break!_[2][4][5][6][7]

## 5. **The Three-Phase Workflow**

| Phase          | Main Action                                    | Roles Involved                               |
|----------------|------------------------------------------------|----------------------------------------------|
| **Research**   | `tech-lead-orchestrator` analyzes requirements | Tech Lead, Project Analyst                   |
| **Planning**   | Main agent creates actionable tasks             | Tech Lead, Team Configurator                 |
| **Execution**  | Agents are invoked in order, passing context   | All relevant Specialists & Core agents       |

**Example (User management feature):**
1. Tech Lead analyzes & returns routing:
   - project-analyst
   - django-backend-expert
   - django-api-developer
2. Main agent invokes only these, in sequence.[2][4][5][6]

## 6. **Agent Return Example / Handoffs**
```markdown
## Task Completed: User API Implementation
- Endpoints created: GET/POST/PUT/DELETE /api/users
- Authentication: JWT with 1-hour expiry
- Roles: admin, user, guest

## Handoff Information
- Next specialist needs: Endpoint URLs and auth header formats
- Specific requirements or constraints: JWT scheme, role structure

## Next Steps
- Recommended next specialist: frontend-developer
- What should be done next: Build a user admin dashboard UI
```
*Your main agent must extract the right context and pass it to the next agent—subagents never communicate directly.*[5][6]

## 7. **Best Practices for Agent Development and Reuse**
- *Single responsibility only*: Each agent masters one domain (API dev, ORM, frontend, etc.).
- *Use XML-style examples* in agent descriptions for smarter invocation (see `creating-agents.md`).
- *Add clear handoff/delegation patterns*
- *Omit `tools` field* for max flexibility: agents inherit all unless restricted purposely.
- *Testing*: Invocation, handoff, end-to-end workflow tests are strongly encouraged[8][9][3]

## 8. **Directory & File Guide**

- **CLAUDE.md**: Technical driver for orchestration/reliability
- **docs/architecture.md**: Deep-dive on structure and real-world workflows[4]
- **docs/orchestration-patterns.md**: Practical orchestration scenarios, context-passing, and advanced patterns[6]
- **docs/agent-team.md**: Coordination realities and illustrative examples of what *actually* happens[5]
- **docs/best-practices.md**: How to write effective, collaborative, and testable agents[8]
- **docs/creating-agents.md**: Agent format, delegation, and testing patterns[9]
- **agents/orchestrators/tech-lead-orchestrator.md**: Tech Lead’s mandatory response and assignment format—*copy for new orchestrators/advanced flows*[7]

## 9. **Extending or Adding Agents**

See `CONTRIBUTING.md` and `docs/creating-agents.md` for:
- Correct YAML & prompt templates
- Example files for each new agent
- How to provide usage/test cases and update documentation
- **Naming:** `framework-domain-specialist` (e.g., `django-api-developer`)
- **Documentation:** Write examples and add the agent to README under the correct group

## 10. **Sample Real-World Usages**

- **E-commerce cart:** Tech Lead assigns Laravel and Vue specialists, orchestrates schema, endpoints, and UI as concrete, sequenced steps
- **Authentication system:** Django backend, API dev, frontend, code review all invoked in strict order
- **Analytics dashboard:** Rails and React stack—different agents drive backend, UI, and performance

**Key:** Agent routes and handoffs must *always* honor `tech-lead-orchestrator` assignments and not shortcut or substitute roles[1][2][4][5][6][7].

## 11. **Common Anti-patterns (Do NOT do these)**
- Do **not** improvise or skip the tech-lead/orchestrator check
- Do **not** select generic agents where the orchestration specifies specialists (e.g., do not use `backend-developer` when `django-backend-expert` is assigned)
- Do **not** allow agents to communicate directly; all data flows through the main agent[2][5]

## 12. **References and Where to Learn More**
- [README.md][1]: Quick intro and team overviews
- [CLAUDE.md][2]: Protocol and required practice for orchestration
- [docs/architecture.md][4]: Deep technical structure
- [docs/agent-team.md][5]: Coordination and handoff detail
- [docs/best-practices.md][8]: Writing and invoking agents
- [docs/creating-agents.md][9]: Agent development and test practice
- [docs/orchestration-patterns.md][6]: End-to-end coordination and advanced flows
- [agents/orchestrators/tech-lead-orchestrator.md][7]: Assignment, task, and execution order template
- [CONTRIBUTING.md][3]: Contribution process & quality standards

**This guide enables efficient, reliable orchestration and collaboration with any Claude subagents using the repo!**  
Copy this as your CLAUDE.md or project documentation to ensure best practices, zero improvisation, and production-grade workflows in Claude Code.
