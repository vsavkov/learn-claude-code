# Quick Start: Containerlab Agent

## Installation

```bash
# Ensure you have the API key set
export ANTHROPIC_API_KEY="your-key-here"

# Or it will be loaded from .env file automatically
```

## Basic Usage

```bash
# Run the agent with a natural language query
python containerlab_agent.py "your question here"
```

## Common Queries

### Infrastructure Overview
```bash
# List all labs
python containerlab_agent.py "show all labs"

# Get lab details
python containerlab_agent.py "inspect my lab"
python containerlab_agent.py "what labs are running?"
```

### Network Analysis
```bash
# Show interfaces
python containerlab_agent.py "show network interfaces"
python containerlab_agent.py "are there any interface issues?"

# Get comprehensive status
python containerlab_agent.py "show me everything about my network"
```

### Visualization
```bash
# Generate diagrams
python containerlab_agent.py "create a mermaid diagram"
python containerlab_agent.py "generate a DOT graph"

# Understanding topology
python containerlab_agent.py "explain my network topology"
```

### Troubleshooting
```bash
# Check health
python containerlab_agent.py "are all nodes healthy?"
python containerlab_agent.py "what interfaces are down?"

# Get recommendations
python containerlab_agent.py "what should I check in my lab?"
```

## What The Agent Can Do

The agent has these capabilities:

1. **list_labs** - List all running containerlab labs
2. **inspect_lab** - Get detailed lab information
3. **inspect_interfaces** - Show network interface details
4. **generate_graph** - Create topology visualizations (DOT/Mermaid)
5. **show_topology_file** - Display topology YAML contents
6. **exec_command** - Execute commands in lab nodes

## Example Session

```bash
$ python containerlab_agent.py "what's running?"

🤖 Containerlab Agent processing: what's running?

I found 1 running lab:

Lab: base-02
- 6 containers running
- All nodes healthy
- Using network-multitool image

Would you like more details?
```

## Advanced Features

### Natural Language Understanding
The agent understands context and intent:
- "what's my network look like?" → inspects topology
- "any problems?" → checks interface status
- "show me a picture" → generates diagram

### Multi-step Queries
Ask complex questions:
```bash
python containerlab_agent.py "list labs, inspect the first one, check if all interfaces are up, and tell me if I need to do anything"
```

### Different Output Formats
Specify how you want to see data:
- Tables (default)
- JSON (for parsing)
- CSV (for spreadsheets)

## Tips

1. **Be conversational** - The agent understands natural language
2. **Ask follow-ups** - It maintains context within a query
3. **Be specific** - Mention lab names if you have multiple labs
4. **Request formats** - Ask for "detailed", "summary", "JSON", etc.

## Troubleshooting

**Agent not responding?**
- Check API key: `echo $ANTHROPIC_API_KEY`
- Verify containerlab works: `clab version`

**No labs found?**
- Deploy a lab: `clab deploy -t topology.yml`
- Check running containers: `docker ps`

**Graph generation fails?**
- Mermaid works without external tools
- DOT requires graphviz: `apt install graphviz`

## Next Steps

1. Run `./example_containerlab_queries.sh` to see examples
2. Read `CONTAINERLAB_AGENT.md` for full documentation
3. Try your own queries!

---

**Pro Tip**: The agent is context-aware. Ask it questions like you would ask a colleague who manages the infrastructure!
