# Agent System Documentation

This directory contains documentation for all agents in the system, organized by functional categories.

## Directory Structure

- **Agent_Management_and_Learning**: Agents responsible for system management, learning, and evolution
- **Architecture_and_System_Design**: Agents focused on system architecture and design
- **Consensus_and_Coordination**: Agents handling consensus protocols and coordination
- **Core_Agents**: Fundamental agents that provide core capabilities
- **Data_and_ML**: Agents specialized in data processing and machine learning
- **Debugging_and_Troubleshooting**: Agents focused on debugging and issue resolution
- **Development_Backend**: Agents specialized in backend development
- **Development_Frontend**: Agents specialized in frontend development
- **Development_General_Coding**: General coding and development agents
- **DevOps_and_CI_CD**: Agents handling DevOps and continuous integration/deployment
- **GitHub_Integration_and_Workflow**: Agents managing GitHub integration and workflows
- **Optimization_and_Performance**: Agents focused on performance optimization
- **Project_Management_and_Planning**: Agents handling project management and planning
- **SPARC_Methodology**: Agents implementing the SPARC methodology
- **Specialized_Mobile**: Agents specialized in mobile development
- **Swarm_and_Collective_Intelligence**: Agents implementing swarm intelligence and collective decision-making
- **Testing_and_QA**: Agents focused on testing and quality assurance

## Key Features

All agents in the system share these capabilities:

1. **Persistent Memory**: Agents can store and retrieve information across sessions
2. **Parallel Processing**: Agents can execute tasks in parallel for improved performance
3. **Context Sharing**: Agents can share context and information with each other
4. **Hooks Integration**: Agents integrate with hooks for extended functionality
5. **Slash Command Access**: Agents can be accessed via slash commands
6. **Prompt Chaining**: Agents can execute complex workflows through prompt chains
7. **MCP Tool Access**: Agents can access external tools and services via MCP servers

## Enhanced Capabilities

### Prompt Chaining
Agents can execute complex multi-step workflows through prompt chaining:
- Sequential execution of related prompts
- Conditional logic for dynamic workflow paths
- Iterative refinement for complex problem solving
- Cross-agent chaining for collaborative workflows

### MCP Tool Integration
Agents can access external tools and services via MCP servers:
- File system operations (read, write, list directories)
- Web search capabilities for current information
- Code execution in sandboxed environments
- Resource management and monitoring tools

## Collaboration

Agents work together through a central Project Orchestration Agent that coordinates tasks and ensures proper collaboration. See the Agent_Collaboration_Framework.md document for details on how agents work together.

## Usage

Each agent documentation file provides:
- Detailed description of the agent's role and responsibilities
- Capabilities and configuration details
- Best practices and methodologies
- Collaboration workflows with other agents
- Integration points and hooks

## Additional Documentation

- **Agent_Collaboration_Framework.md**: Comprehensive guide to how agents work together
- **Prompt_Chaining_and_MCP_Integration.md**: Detailed information on prompt chaining and MCP tool access