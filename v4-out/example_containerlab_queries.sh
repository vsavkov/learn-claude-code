#!/bin/bash
# Example queries for the Containerlab Infrastructure Agent
# Run these examples to see what the agent can do

echo "======================================"
echo "Containerlab Agent Example Queries"
echo "======================================"
echo ""

echo "1. List all running labs"
python containerlab_agent.py "list all running labs"
echo ""
echo "Press Enter to continue..."
read

echo "2. Inspect lab details"
python containerlab_agent.py "show me detailed information about my lab"
echo ""
echo "Press Enter to continue..."
read

echo "3. Show network interfaces"
python containerlab_agent.py "show me the network interfaces and tell me if there are any issues"
echo ""
echo "Press Enter to continue..."
read

echo "4. Generate Mermaid diagram"
python containerlab_agent.py "create a mermaid diagram of the topology"
echo ""
echo "Press Enter to continue..."
read

echo "5. Complex query"
python containerlab_agent.py "what is the network topology, are all nodes healthy, and what might need attention?"
echo ""

echo "======================================"
echo "Examples complete!"
echo "======================================"
