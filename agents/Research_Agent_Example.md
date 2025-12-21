# Example: Research Agent with Prompt Chaining and MCP Integration

This document demonstrates how the Researcher agent can leverage prompt chaining and MCP tools to conduct comprehensive research.

## Scenario
The Researcher agent is tasked with investigating the latest trends in React Native performance optimization for a mobile application project.

## Prompt Chain Implementation

### Chain Definition
```yaml
chain:
  name: "React Native Performance Research"
  steps:
    - step: "trend-analysis"
      prompt: "Analyze current trends in React Native performance optimization for 2025"
      next: "technical-deep-dive"
    
    - step: "technical-deep-dive"
      prompt: "Provide technical details on the top 3 performance optimization techniques identified"
      next: "benchmark-research"
    
    - step: "benchmark-research"
      prompt: "Research benchmark data comparing these techniques"
      next: "tool-evaluation"
    
    - step: "tool-evaluation"
      prompt: "Evaluate tools that can help implement these optimizations"
      next: "implementation-planning"
    
    - step: "implementation-planning"
      prompt: "Create an implementation plan for applying these optimizations to our project"
      next: "documentation"
    
    - step: "documentation"
      prompt: "Document findings in a comprehensive report format"
      next: null
```

## MCP Tool Integration

### Web Search for Current Information
```python
# Search for recent React Native performance articles
search_results = mcp_web_search(
    query="React Native performance optimization techniques 2025",
    max_results=10
)

# Process search results
processed_results = llm_process_search_results(search_results)
```

### File System Operations
```python
# Read existing project files to understand context
package_json = mcp_read_file("package.json")
app_js = mcp_read_file("src/App.js")
config_files = mcp_list_directory("config/")

# Analyze project structure
project_analysis = llm_analyze_project_structure(
    package_json=package_json,
    main_files=[app_js],
    config_files=config_files
)
```

### Code Execution for Validation
```python
# Run performance benchmarking tools
benchmark_result = mcp_execute_code(
    command="npx react-native-performance-benchmark",
    working_directory="/project",
    timeout=600
)

# Process benchmark results
performance_analysis = llm_analyze_benchmark_results(benchmark_result)
```

## Complete Workflow Example

### Step 1: Initial Research with Web Search
```markdown
Agent Action:
1. mcp_web_search("React Native performance optimization 2025 latest techniques")
2. LLM processes search results to identify key trends
3. Store findings in persistent memory
```

### Step 2: Technical Deep Dive
```markdown
Agent Action:
1. Access stored research findings
2. LLM analyzes technical details of top techniques
3. mcp_read_file("docs/tech-stack.md") to understand project context
4. Store technical analysis in persistent memory
```

### Step 3: Benchmark Research
```markdown
Agent Action:
1. Access technical analysis from previous step
2. mcp_web_search("React Native performance benchmarks 2025 comparison")
3. LLM synthesizes benchmark data with technical analysis
4. Store benchmark findings in persistent memory
```

### Step 4: Tool Evaluation
```markdown
Agent Action:
1. Access benchmark findings
2. mcp_read_file("package.json") to check existing tools
3. LLM evaluates additional tools based on research
4. mcp_execute_code("npm info react-native-performance-tools") to get tool info
5. Store tool evaluation in persistent memory
```

### Step 5: Implementation Planning
```markdown
Agent Action:
1. Access all previous research findings
2. mcp_list_directory("src/components/") to understand project structure
3. LLM creates implementation plan based on project context
4. Store implementation plan in persistent memory
```

### Step 6: Documentation
```markdown
Agent Action:
1. Access all research findings and plans
2. LLM synthesizes comprehensive report
3. mcp_write_file("docs/performance-research-report.md", report_content)
4. Share report with Project Manager agent
```

## Cross-Agent Collaboration

### Chain Initiation by Project Manager
```markdown
Project Manager:
"/researcher investigate React Native performance optimization for mobile app project"

Researcher:
1. Receives task from Project Manager
2. Initiates prompt chain for comprehensive research
3. Uses MCP tools for current information gathering
4. Reports findings back to Project Manager
```

### Chain Handoff to Mobile Developer
```markdown
Researcher:
"/mobile-dev here are the React Native performance optimization techniques we should implement: [findings]"

Mobile Developer:
1. Receives research findings
2. Initiates implementation chain
3. Uses MCP tools to apply optimizations
4. Reports progress to Project Manager
```

## Benefits of Enhanced Capabilities

### Improved Research Quality
- Access to current information through web searches
- Technical validation through code execution
- Context-aware analysis through file system operations

### Enhanced Efficiency
- Automated workflow through prompt chaining
- Parallel execution of independent research tasks
- Reusable chain templates for similar research tasks

### Better Integration
- Seamless collaboration between research and implementation
- Context preservation across agent boundaries
- Consistent documentation through standardized chains

### Continuous Learning
- Research patterns stored in persistent memory
- Tool effectiveness tracked over time
- Chain optimization based on past performance

This example demonstrates how the combination of prompt chaining and MCP tool integration enables agents to perform complex tasks that would be impossible with LLM reasoning alone.