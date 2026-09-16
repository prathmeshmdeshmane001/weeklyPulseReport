# MCP Integration Plan

## Overview

This document defines how the project will use MCP (Model Context Protocol) servers or connectors to interact with Google Docs and Gmail. The project must follow an MCP-first integration approach and avoid building custom OAuth clients or direct Google REST API integrations.

## What is MCP

MCP (Model Context Protocol) provides a standard way for AI agents to call external tools. MCP servers expose structured tool interfaces that the agent can invoke to perform actions such as creating documents, reading files, or sending emails.

Using MCP means:

- The agent calls a tool provided by the MCP server
- The MCP server handles authentication and API communication
- The agent does not manage tokens, OAuth flows, or HTTP requests directly

## Required MCP Integrations

### 1. Google Docs MCP

**Purpose:** Create or update the weekly pulse document.

**Expected MCP Tool Capabilities:**

| Capability | Description |
|------------|-------------|
| Create document | Create a new Google Docs document with a title |
| Write content | Insert the weekly pulse text into the document |
| Update document | Update an existing document with new weekly content |
| Get document link | Retrieve the shareable URL of the document |

**How the Agent Uses It:**

1. After generating the weekly pulse, the agent calls the Google Docs MCP tool
2. The tool creates a new document or updates an existing one
3. The weekly pulse content is inserted into the document
4. The document link is captured for use in the Gmail draft

### 2. Gmail MCP

**Purpose:** Create a draft email containing the weekly pulse or a link to the Google Docs report.

**Expected MCP Tool Capabilities:**

| Capability | Description |
|------------|-------------|
| Create draft | Create a new Gmail draft message |
| Set recipient | Set the email recipient (self or alias) |
| Set subject | Set the email subject line |
| Set body | Set the email body content |

**How the Agent Uses It:**

1. After the Google Docs document is created, the agent calls the Gmail MCP tool
2. The tool creates a draft email with a clear subject and body
3. The body contains the weekly pulse text or a link to the Google Docs document
4. The draft is addressed to the user or an approved alias

## Integration Flow

```text
AI Agent generates weekly pulse
        |
        v
Agent calls Google Docs MCP tool
        |
        +--> Creates or updates document
        +--> Returns document link
        |
        v
Agent calls Gmail MCP tool
        |
        +--> Creates draft email
        +--> Includes pulse or document link
        |
        v
Delivery complete
```

## What We Are NOT Doing

- **No custom Google OAuth client** — MCP handles authentication
- **No direct Google Docs REST API calls** — use MCP tool instead
- **No direct Gmail REST API calls** — use MCP tool instead
- **No manual token management** — MCP manages credentials

## MCP Server Selection

The specific MCP servers or connectors will depend on what the development environment provides. The requirement is:

- Use MCP-compatible tools for Google Docs and Gmail
- Confirm tool availability before Phase 9 and Phase 10

## Configuration Needed

Before integration phases begin, the following must be confirmed:

- [ ] Google Docs MCP server is available and accessible
- [ ] Gmail MCP server is available and accessible
- [ ] MCP tools support document creation and draft email creation
- [ ] Authentication is handled by the MCP server (not by the project)

## Phase Mapping

| Phase | MCP Usage |
|-------|-----------|
| Phase 9: Google Docs Delivery | Google Docs MCP — create/update pulse document |
| Phase 10: Gmail Draft Creation | Gmail MCP — create draft email with pulse or link |
