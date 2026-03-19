# Scholar Flow Architecture

## Overview

Scholar Flow is a pipeline of specialized AI agents that automate academic research methodology. The system is built on three layers: agents, skills, and MCP servers.

> TODO: Expand from design spec

## Agent Layer

The agent layer consists of 11 specialized agents coordinated by the Orchestrator. Each agent handles one phase of the research pipeline.

> TODO: Detail each agent's role and how they chain together

## Skill Layer

Skills are the knowledge layer — markdown files that encode domain expertise. Agents load relevant skills based on the project's discipline, methodology, and target journal.

> TODO: Document skill selection algorithm and loading mechanism

## MCP Server Layer

MCP servers provide agents with access to external APIs and tools (PubMed, arXiv, statistics engines, etc.).

> TODO: Document each MCP server's capabilities and configuration

## Context Window Management

Each agent produces a SUMMARY.md alongside its full output. Downstream agents consume summaries by default and read full files only when deeper detail is needed.

> TODO: Document token budget strategy

## Project State Management

Each academic project is stored in a structured directory under `docs/academic-projects/`. The Orchestrator tracks project status in PROJECT.md.

> TODO: Document directory structure and state transitions

## Failure Modes and Recovery

Each agent has defined failure modes with recovery strategies.

> TODO: Document failure table from design spec
