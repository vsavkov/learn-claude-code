# 🤖 Containerlab Infrastructure Agent

> An AI-powered agent that helps you visualize, inspect, and manage containerlab network topologies using natural language.

## 🚀 Quick Start

```bash
# Basic usage
python containerlab_agent.py "show all running labs"

# Get help
python containerlab_agent.py "what can you do?"

# Complex analysis
python containerlab_agent.py "give me a complete overview of my infrastructure"
```

## 📚 Documentation

- **[Quick Start Guide](QUICK_START_CONTAINERLAB.md)** - Get started in 5 minutes
- **[Full Documentation](CONTAINERLAB_AGENT.md)** - Complete reference
- **[Summary](CONTAINERLAB_AGENT_SUMMARY.md)** - What was built and why
- **[Examples Script](example_containerlab_queries.sh)** - Interactive examples

## ✨ What It Does

Transform this:
```bash
clab inspect --all
clab inspect --name mylab --wide
clab inspect interfaces --name mylab
clab graph --name mylab --dot
# ...manual analysis of outputs...
```

Into this:
```bash
python containerlab_agent.py "show me my infrastructure and tell me what needs attention"
```

## 🎯 Key Features

- 📋 **List labs** - See all running containerlab environments
- 🔍 **Inspect details** - Deep dive into lab configurations
- 🌐 **Interface analysis** - Check network connectivity
- 📊 **Topology graphs** - Visualize with Mermaid or DOT
- ⚠️ **Issue detection** - Automatically find problems
- 💬 **Natural language** - Talk to your infrastructure

## 🛠️ Agent Capabilities

The agent has 6 core tools:

1. **list_labs** - List all running labs
2. **inspect_lab** - Get detailed lab information  
3. **inspect_interfaces** - Show network interface details
4. **generate_graph** - Create topology visualizations
5. **show_topology_file** - Display YAML configurations
6. **exec_command** - Execute commands in lab nodes

## 📖 Example Queries

### Simple
```bash
python containerlab_agent.py "what labs are running?"
python containerlab_agent.py "show me the network interfaces"
python containerlab_agent.py "create a diagram"
```

### Advanced
```bash
python containerlab_agent.py "are all my nodes healthy?"
python containerlab_agent.py "what's the topology and are there any issues?"
python containerlab_agent.py "show me everything and recommend next steps"
```

## 🎓 Example Output

```
$ python containerlab_agent.py "show all labs"

🤖 Containerlab Agent processing: show all labs

I found 1 running lab:

Lab: base-02
- Topology file: ../containerlab/topo/base-02/topology.clab.yml
- Total nodes: 6 containers
- Status: All running

Nodes:
1. clab-base-02-h1 - Linux host (network-multitool)
2. clab-base-02-h2 - Linux host (network-multitool)
3. clab-base-02-sw-h1 - Linux switch (network-multitool)
4. clab-base-02-sw-h2 - Linux switch (network-multitool)
5. clab-base-02-sw1 - Linux switch (network-multitool)
6. clab-base-02-sw2 - Linux switch (network-multitool)

All nodes are running and have IPv4/IPv6 addresses assigned.
Would you like detailed information about any of these nodes?
```

## 🏗️ Architecture

Built using the minimal agent pattern:

```
┌─────────────┐
│ User Query  │ "show my infrastructure"
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Claude AI     │ Decides what tools to use
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Tool Executor  │ Runs containerlab commands
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Analysis      │ Interprets results
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Response      │ Helpful, contextualized answer
└─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Containerlab installed (`clab` command)
- Anthropic API key
- `anthropic` Python package

## 🔧 Installation

1. **Clone or navigate to the repository**
```bash
cd /home/vs/projects/learn-claude-code
```

2. **Set up API key**
```bash
export ANTHROPIC_API_KEY="your-api-key"
# Or add to .env file - it will be loaded automatically
```

3. **Install dependencies**
```bash
pip install anthropic
```

4. **Run the agent**
```bash
python containerlab_agent.py "show all labs"
```

## 🎬 Try It Out

Run the interactive examples:
```bash
./example_containerlab_queries.sh
```

## 🧠 Design Philosophy

This agent follows key principles:

1. **Model IS the agent** - Claude decides what to do, not hardcoded workflows
2. **Capabilities enable** - Simple, composable tools
3. **Trust the model** - Let AI figure out the best approach
4. **Progressive complexity** - Start simple, handles complex queries naturally
5. **Clean context** - Clear tool descriptions and outputs

## 🌟 Real-World Example

The agent can perform complex analysis automatically:

```bash
$ python containerlab_agent.py "give me a complete overview including issues"

# Agent automatically:
# 1. Lists all labs
# 2. Inspects detailed configuration
# 3. Checks all interface statuses
# 4. Generates topology diagram
# 5. Analyzes for issues
# 6. Provides recommendations

# Output:
## Complete Infrastructure Overview - Lab "base-02"

### Issues Requiring Attention
⚠️ CRITICAL: SW2 Switch Has Multiple Down Interfaces
- br0 (bridge): DOWN
- eth1: DOWN (link to sw-h1:eth3)
- eth2: DOWN (link to sw-h2:eth3)

Impact: Network has no redundancy...

### Recommended Actions
1. Investigate sw2 bridge status
2. Bring up interfaces
3. Test redundant paths
...
```

## 🔬 Technical Details

- **AI Model**: Claude Sonnet 4.5
- **API**: Anthropic Messages API with tool use
- **Backend**: Containerlab CLI (`clab`)
- **Language**: Python 3.8+
- **Architecture**: Stateless, tool-based agent

## 📊 Performance

- Simple queries: 2-5 seconds
- Complex multi-tool queries: 5-10 seconds
- No caching needed (stateless)
- Handles multiple labs efficiently

## 🤝 Contributing

Want to add more capabilities? Easy!

1. Add tool definition to `TOOLS` list
2. Implement the function
3. Add to `process_tool_call()`
4. Claude automatically learns to use it!

## 📝 Files Overview

```
containerlab_agent.py              # Main agent (420 lines)
CONTAINERLAB_AGENT.md              # Full documentation
QUICK_START_CONTAINERLAB.md        # Quick start guide
CONTAINERLAB_AGENT_SUMMARY.md      # Technical summary
example_containerlab_queries.sh    # Example queries
README_CONTAINERLAB_AGENT.md       # This file
```

## 🎯 Use Cases

- **DevOps**: Quick infrastructure checks
- **Debugging**: Find interface issues fast
- **Documentation**: Generate topology diagrams
- **Learning**: Understand network layouts
- **Automation**: Script-friendly JSON output
- **Monitoring**: Health checks and status

## ⚡ Why This Matters

Traditional approach:
- Remember specific commands and flags
- Run multiple commands manually
- Parse and correlate outputs yourself
- Look up documentation frequently

With this agent:
- Ask questions in natural language
- Agent orchestrates multiple tools
- Get analyzed, actionable insights
- Context-aware recommendations

## 🔮 Future Possibilities

- Lab deployment/destruction
- Configuration management  
- Real-time monitoring integration
- Automated troubleshooting
- Performance metrics
- Multi-lab comparisons
- Compliance checking

## 📖 Learn More

- [Containerlab Documentation](https://containerlab.dev/)
- [Anthropic Claude API](https://www.anthropic.com/)
- [Agent Design Philosophy](skills/agent-builder/SKILL.md)

## 🎓 Educational Value

This agent demonstrates:
- ✅ How to build AI agents with Claude
- ✅ Tool use and orchestration patterns
- ✅ Natural language interface design
- ✅ Infrastructure automation
- ✅ Minimal agent architecture

## 💡 Tips

1. **Be conversational** - "what's up with my network?" works!
2. **Ask follow-ups** - Context is maintained
3. **Be specific when needed** - Mention lab names
4. **Request formats** - Ask for JSON, tables, diagrams

## 🐛 Troubleshooting

**No labs found?**
```bash
clab deploy -t topology.yml
```

**API errors?**
```bash
echo $ANTHROPIC_API_KEY  # Check it's set
```

**Containerlab issues?**
```bash
clab version  # Verify installation
```

## 📄 License

Same as parent project.

---

**Built with** ❤️ **using Claude AI and the minimal agent pattern**

**Questions?** Just ask the agent! 😊
```bash
python containerlab_agent.py "what can you help me with?"
```

## API Gateway

A query-only HTTP gateway is available via FastAPI.

### Start

```bash
pip install -r requirements.txt
uvicorn api_gateway:app --host 127.0.0.1 --port 8080
```

### Example request

```bash
curl -s http://127.0.0.1:8080/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"show all running labs"}'
```

### Docs

See `API_GATEWAY.md` for schema details and response format.

## Next.js Web UI (via Dedicated BFF)

This project now includes:

- `bff/`: Express + TypeScript server that calls FastAPI gateway
- `ui/`: Next.js dashboard/chat UI that calls only BFF endpoints

### Start Gateway

```bash
uvicorn api_gateway:app --host 127.0.0.1 --port 8080
```

### Start BFF

```bash
cd bff
npm install
npm run dev
```

### Start UI

```bash
cd ui
npm install
npm run dev
```

### Open UI

```text
http://127.0.0.1:3000
```

For full details, see `WEB_UI.md`.

## FE App (No CORS, Single Origin)

Use `fe/` when you want one application to serve UI and translate API requests to the gateway without browser CORS.

### Start Gateway

```bash
uvicorn api_gateway:app --host 127.0.0.1 --port 8080
```

### Start FE

```bash
cd fe
npm install
npm run dev
```

### Open FE

```text
http://127.0.0.1:3000
```

See `FE.md` for architecture and API details.
