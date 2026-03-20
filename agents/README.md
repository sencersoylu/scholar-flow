# Scholar Flow Agents

Agents are the workers in the Scholar Flow pipeline. Each agent is a Claude Code subagent specialized in one phase of the academic research workflow.

## How Agents Work

The **Orchestrator** is the main agent that interacts with you. It dispatches specialized agents based on where you are in the research pipeline. Each agent:

1. Loads relevant **skills** (methodology protocols, discipline standards)
2. Uses **MCP servers** to access external tools and APIs
3. Reads prior agent outputs from the project directory
4. Produces structured output files
5. Writes a `SUMMARY.md` for downstream agents

## Agent Template

Each agent definition follows this structure:

- **Role** — One sentence describing what this agent does
- **Skills Loaded** — List of skills this agent consumes
- **MCP Tools** — List of MCP servers this agent uses
- **Input** — What this agent expects to receive
- **Process** — Step-by-step description of what the agent does
- **Output** — Files this agent produces (with paths)
- **User Interaction** — When and what this agent asks the user (if applicable)
- **Failure Modes** — What can go wrong and how the agent handles it

## Skill References

Skills use a folder-based structure: `skills/<category>/<skill-name>/SKILL.md`. Some skills include runnable Python scripts in their `scripts/` subdirectory. When an agent loads a skill, it reads the `SKILL.md` file and may invoke associated scripts for analysis tasks.

## Creating a New Agent

1. Copy the template into a new `.md` file in this directory
2. Fill in all sections
3. Register the agent in the Orchestrator's dispatch table
4. Add tests for the agent's expected behavior
