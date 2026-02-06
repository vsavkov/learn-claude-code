#!/usr/bin/env python3
"""
Containerlab Infrastructure Agent

An AI agent that helps visualize and manage containerlab infrastructure.
It can inspect running labs, show topology details, display graphs, and more.

Usage:
    python containerlab_agent.py "show all running labs"
    python containerlab_agent.py "inspect the lab topology"
    python containerlab_agent.py "show me the network graph"
"""

import anthropic
import os
import sys
import json
import subprocess
from typing import Any
from pathlib import Path

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key not in os.environ:
                    os.environ[key] = value


# Containerlab capabilities
TOOLS = [
    {
        "name": "list_labs",
        "description": "List all running containerlab labs. Shows lab names, number of containers, and basic status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["table", "json", "csv"],
                    "description": "Output format for the lab listing",
                    "default": "table"
                }
            }
        }
    },
    {
        "name": "inspect_lab",
        "description": "Inspect detailed information about a specific containerlab lab or all labs. Returns container details, network info, and configuration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lab_name": {
                    "type": "string",
                    "description": "Name of the lab to inspect. If not provided, inspects all running labs"
                },
                "format": {
                    "type": "string",
                    "enum": ["table", "json", "csv"],
                    "description": "Output format",
                    "default": "table"
                },
                "wide": {
                    "type": "boolean",
                    "description": "Show more details about the lab and its nodes",
                    "default": False
                },
                "details": {
                    "type": "boolean",
                    "description": "Print all details in JSON format, grouped by lab",
                    "default": False
                }
            }
        }
    },
    {
        "name": "inspect_interfaces",
        "description": "Inspect network interfaces of nodes in a containerlab lab. Shows interface names, IP addresses, and connections.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lab_name": {
                    "type": "string",
                    "description": "Name of the lab"
                },
                "node_name": {
                    "type": "string",
                    "description": "Specific node to inspect. If not provided, shows all nodes"
                },
                "format": {
                    "type": "string",
                    "enum": ["table", "json", "csv"],
                    "description": "Output format",
                    "default": "table"
                }
            }
        }
    },
    {
        "name": "generate_graph",
        "description": "Generate a topology graph visualization. Can create DOT file, start web server, or output Mermaid diagram. Note: Direct PNG/SVG generation requires external tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lab_name": {
                    "type": "string",
                    "description": "Name of the lab to generate graph for"
                },
                "format": {
                    "type": "string",
                    "enum": ["dot", "mermaid", "server"],
                    "description": "Output format: 'dot' for DOT file, 'mermaid' for Mermaid diagram, 'server' to start web server",
                    "default": "dot"
                },
                "output_file": {
                    "type": "string",
                    "description": "Output file path for DOT format",
                    "default": "topology.dot"
                }
            }
        }
    },
    {
        "name": "show_topology_file",
        "description": "Display the contents of a containerlab topology YAML file. Useful for understanding lab configuration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topo_file": {
                    "type": "string",
                    "description": "Path to the topology YAML file"
                }
            },
            "required": ["topo_file"]
        }
    },
    {
        "name": "exec_command",
        "description": "Execute a command inside one or more containerlab nodes. Useful for checking node status or gathering information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lab_name": {
                    "type": "string",
                    "description": "Name of the lab"
                },
                "node_name": {
                    "type": "string",
                    "description": "Name of the node(s). Can use 'all' for all nodes"
                },
                "command": {
                    "type": "string",
                    "description": "Command to execute inside the node(s)"
                }
            },
            "required": ["command"]
        }
    }
]


def run_command(cmd: list[str]) -> dict[str, Any]:
    """Execute a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def list_labs(format: str = "table") -> str:
    """List all running containerlab labs."""
    cmd = ["clab", "inspect", "--all", "--format", format]
    result = run_command(cmd)
    
    if result["success"]:
        return result["stdout"] if result["stdout"] else "No labs currently running"
    else:
        return f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}"


def inspect_lab(lab_name: str = None, format: str = "table", wide: bool = False, details: bool = False) -> str:
    """Inspect a containerlab lab."""
    cmd = ["clab", "inspect"]
    
    if lab_name:
        cmd.extend(["--name", lab_name])
    else:
        cmd.append("--all")
    
    cmd.extend(["--format", format])
    
    if wide:
        cmd.append("--wide")
    
    if details:
        cmd.append("--details")
    
    result = run_command(cmd)
    
    if result["success"]:
        return result["stdout"] if result["stdout"] else "No lab information available"
    else:
        return f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}"


def inspect_interfaces(lab_name: str = None, node_name: str = None, format: str = "table") -> str:
    """Inspect interfaces of containerlab nodes."""
    cmd = ["clab", "inspect", "interfaces"]
    
    if lab_name:
        cmd.extend(["--name", lab_name])
    
    if node_name:
        cmd.extend(["--node", node_name])
    
    cmd.extend(["--format", format])
    
    result = run_command(cmd)
    
    if result["success"]:
        return result["stdout"] if result["stdout"] else "No interface information available"
    else:
        return f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}"


def generate_graph(lab_name: str = None, format: str = "dot", output_file: str = "topology.dot") -> str:
    """Generate a topology graph."""
    cmd = ["clab", "graph"]
    
    if lab_name:
        cmd.extend(["--name", lab_name])
    
    if format == "dot":
        cmd.append("--dot")
        result = run_command(cmd)
        if result["success"]:
            # The DOT file is created in the lab directory automatically
            # Extract the path from stderr/stdout
            output = result["stdout"] + result["stderr"]
            return f"DOT graph generated successfully!\n\n{output}\n\nYou can convert it to PNG with:\n  dot -Tpng <path-to-dot-file> -o topology.png"
        else:
            return f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}"
    
    elif format == "mermaid":
        cmd.append("--mermaid")
        result = run_command(cmd)
        if result["success"]:
            return f"Mermaid diagram:\n\n{result['stdout']}"
        else:
            return f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}"
    
    elif format == "server":
        return "To start the graph web server, run manually: clab graph --name <lab-name>\nThe web interface will be available at http://localhost:50080"
    
    else:
        return f"Unknown format: {format}"


def show_topology_file(topo_file: str) -> str:
    """Display the contents of a topology file."""
    try:
        with open(topo_file, 'r') as f:
            content = f.read()
        return f"Topology file: {topo_file}\n\n{content}"
    except FileNotFoundError:
        return f"Error: Topology file not found: {topo_file}"
    except Exception as e:
        return f"Error reading topology file: {str(e)}"


def exec_command(command: str, lab_name: str = None, node_name: str = None) -> str:
    """Execute a command in containerlab nodes."""
    cmd = ["clab", "exec"]
    
    if lab_name:
        cmd.extend(["--name", lab_name])
    
    if node_name:
        cmd.extend(["--node", node_name])
    
    cmd.extend(["--cmd", command])
    
    result = run_command(cmd)
    
    if result["success"]:
        return result["stdout"] if result["stdout"] else "Command executed (no output)"
    else:
        return f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}"


def process_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Process a tool call and return the result."""
    
    if tool_name == "list_labs":
        return list_labs(**tool_input)
    
    elif tool_name == "inspect_lab":
        return inspect_lab(**tool_input)
    
    elif tool_name == "inspect_interfaces":
        return inspect_interfaces(**tool_input)
    
    elif tool_name == "generate_graph":
        return generate_graph(**tool_input)
    
    elif tool_name == "show_topology_file":
        return show_topology_file(**tool_input)
    
    elif tool_name == "exec_command":
        return exec_command(**tool_input)
    
    else:
        return f"Unknown tool: {tool_name}"


def run_agent(user_message: str) -> str:
    """Run the containerlab agent with a user message."""
    
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    system_prompt = """You are a containerlab infrastructure assistant. You help users understand, 
visualize, and manage their containerlab network topologies.

You have access to tools that can:
- List all running labs
- Inspect lab details, nodes, and configurations
- Show network interface information
- Generate topology graphs
- Display topology file contents
- Execute commands inside containerlab nodes

When a user asks about their containerlab infrastructure:
1. Use the appropriate tools to gather information
2. Present the information clearly and concisely
3. Offer helpful insights about the topology
4. Suggest useful next steps if appropriate

Be proactive in using tools to provide complete answers. If you need to check multiple things
to fully answer a question, use multiple tools in sequence."""

    messages = [{"role": "user", "content": user_message}]
    
    # Agent loop
    while True:
        response = client.messages.create(
            model=os.getenv("MODEL_ID", "claude-sonnet-4-5-20250929"),
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )
        
        # Add assistant response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # Check if we're done
        if response.stop_reason == "end_turn":
            # Extract text responses
            text_responses = [block.text for block in response.content if hasattr(block, "text")]
            return "\n".join(text_responses)
        
        # Process tool calls
        if response.stop_reason == "tool_use":
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    
                    print(f"\n[Using tool: {tool_name}]", file=sys.stderr)
                    
                    result = process_tool_call(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason
            return f"Agent stopped unexpectedly: {response.stop_reason}"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Containerlab Infrastructure Agent")
        print("\nUsage:")
        print("  python containerlab_agent.py \"your question about containerlab\"")
        print("\nExamples:")
        print("  python containerlab_agent.py \"show all running labs\"")
        print("  python containerlab_agent.py \"inspect my lab topology\"")
        print("  python containerlab_agent.py \"show the network interfaces\"")
        print("  python containerlab_agent.py \"generate a topology graph\"")
        sys.exit(1)
    
    user_message = " ".join(sys.argv[1:])
    
    print(f"🤖 Containerlab Agent processing: {user_message}\n")
    
    result = run_agent(user_message)
    print(result)


if __name__ == "__main__":
    main()
