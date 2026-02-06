# Containerlab Infrastructure Agent

An AI-powered agent that helps you visualize, inspect, and manage containerlab network topologies.

## Overview

This agent uses Claude AI to interact with containerlab infrastructure through natural language. It can:

- 📋 List all running containerlab labs
- 🔍 Inspect detailed lab information
- 🌐 Show network interface configurations
- 📊 Generate topology graphs
- 📄 Display topology file contents
- 🖥️ Execute commands inside containerlab nodes

## Prerequisites

- Python 3.8+
- Containerlab installed and accessible via `clab` command
- Anthropic API key set in environment variable `ANTHROPIC_API_KEY`

## Installation

1. Ensure containerlab is installed:
```bash
clab version
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

3. Install Python dependencies:
```bash
pip install anthropic
```

## Usage

The agent accepts natural language queries about your containerlab infrastructure:

### Basic Commands

```bash
# List all running labs
python containerlab_agent.py "show all running labs"

# Inspect a specific lab
python containerlab_agent.py "inspect my lab"

# Show network interfaces
python containerlab_agent.py "show me the network interfaces"

# Generate a topology graph
python containerlab_agent.py "create a topology graph"

# Get detailed information
python containerlab_agent.py "give me detailed information about all labs"
```

### Advanced Queries

```bash
# Ask for specific information
python containerlab_agent.py "what nodes are in my lab and what are their IPs?"

# Get recommendations
python containerlab_agent.py "show me the topology and suggest what I should check"

# Multiple operations
python containerlab_agent.py "list all labs, then show details of the first one"
```

## Agent Capabilities

The agent has access to the following tools:

### 1. **list_labs**
Lists all running containerlab labs with basic status information.

### 2. **inspect_lab**
Provides detailed information about labs including:
- Container details
- Network configuration
- Node status
- Management addresses

### 3. **inspect_interfaces**
Shows network interface information:
- Interface names
- IP addresses
- Connections between nodes

### 4. **generate_graph**
Creates visual topology graphs in various formats:
- PNG images
- SVG vector graphics
- DOT format files

### 5. **show_topology_file**
Displays the YAML topology file contents for understanding lab configuration.

### 6. **exec_command**
Executes commands inside containerlab nodes for gathering information or checking status.

## How It Works

The agent follows a simple but powerful loop:

1. **Understand**: Claude analyzes your natural language request
2. **Plan**: Decides which containerlab tools to use
3. **Execute**: Runs the appropriate `clab` commands
4. **Analyze**: Interprets the results
5. **Respond**: Provides a clear, helpful answer

The agent can chain multiple tool calls together to answer complex questions.

## Examples

### Example 1: Quick Overview
```bash
$ python containerlab_agent.py "what labs are running?"

🤖 Containerlab Agent processing: what labs are running?

Currently, there are X labs running:
1. lab-name-1 - 5 containers
2. lab-name-2 - 3 containers

Would you like detailed information about any of these labs?
```

### Example 2: Detailed Inspection
```bash
$ python containerlab_agent.py "show me complete details about my lab"

🤖 Containerlab Agent processing: show me complete details about my lab

[Detailed table showing all nodes, their states, interfaces, and connections]
```

### Example 3: Visualization
```bash
$ python containerlab_agent.py "create a PNG graph of my topology"

🤖 Containerlab Agent processing: create a PNG graph of my topology

I've generated a topology graph and saved it as topology.png. 
The graph shows X nodes connected in a Y topology...
```

## Design Philosophy

This agent follows the minimal agent pattern:

- **Model-driven**: Claude decides what to do, not hardcoded workflows
- **Tool-enabled**: Simple, atomic capabilities that can be combined
- **Trust-based**: The model figures out the best way to answer questions
- **Progressive**: Start simple, the agent adapts to complex queries

## Troubleshooting

**"Command not found: clab"**
- Ensure containerlab is installed: `sudo containerlab install`

**"No labs currently running"**
- Deploy a lab first: `clab deploy -t topology.yml`

**"API key not found"**
- Set the environment variable: `export ANTHROPIC_API_KEY="your-key"`

**Agent not responding**
- Check your API key is valid
- Ensure you have network connectivity
- Verify containerlab is accessible

## Extending the Agent

To add new capabilities:

1. Add a new tool definition to the `TOOLS` list
2. Implement the corresponding function
3. Add the function to `process_tool_call()`

The agent will automatically learn to use new tools based on their descriptions.

## License

Same as the parent project.

## Credits

Built using:
- [Anthropic Claude API](https://www.anthropic.com/)
- [Containerlab](https://containerlab.dev/)
- Agent design patterns from this repository
