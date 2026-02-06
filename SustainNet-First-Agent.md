# SustainNet First Agent

At the end of deployment the `containerlab` outputs the table of hosts and switches.

```
╭────────────────────┬────────────────────────────────────────┬─────────┬───────────────────╮
│        Name        │               Kind/Image               │  State  │   IPv4/6 Address  │
├────────────────────┼────────────────────────────────────────┼─────────┼───────────────────┤
│ clab-base-02-h1    │ linux                                  │ running │ 172.20.20.3       │
│                    │ ghcr.io/hellt/network-multitool:latest │         │ 3fff:172:20:20::3 │
├────────────────────┼────────────────────────────────────────┼─────────┼───────────────────┤
│ clab-base-02-h2    │ linux                                  │ running │ 172.20.20.2       │
│                    │ ghcr.io/hellt/network-multitool:latest │         │ 3fff:172:20:20::2 │
├────────────────────┼────────────────────────────────────────┼─────────┼───────────────────┤
│ clab-base-02-sw-h1 │ linux                                  │ running │ 172.20.20.5       │
│                    │ ghcr.io/hellt/network-multitool:latest │         │ 3fff:172:20:20::5 │
├────────────────────┼────────────────────────────────────────┼─────────┼───────────────────┤
│ clab-base-02-sw-h2 │ linux                                  │ running │ 172.20.20.7       │
│                    │ ghcr.io/hellt/network-multitool:latest │         │ 3fff:172:20:20::7 │
├────────────────────┼────────────────────────────────────────┼─────────┼───────────────────┤
│ clab-base-02-sw1   │ linux                                  │ running │ 172.20.20.6       │
│                    │ ghcr.io/hellt/network-multitool:latest │         │ 3fff:172:20:20::6 │
├────────────────────┼────────────────────────────────────────┼─────────┼───────────────────┤
│ clab-base-02-sw2   │ linux                                  │ running │ 172.20.20.4       │
│                    │ ghcr.io/hellt/network-multitool:latest │         │ 3fff:172:20:20::4 │
╰────────────────────┴────────────────────────────────────────┴─────────┴───────────────────╯
```

## Examples of our first agent functionality

### Show all labs
Command:
```
python containerlab_agent.py "show all labs"
```
Output:
```
I found **1 running lab** in your containerlab environment:

## Lab: **base-02**
- **Topology file**: `../../containerlab/topo/base-02/topology.clab.yml`
- **Status**: All nodes running ✓
- **Total nodes**: 6

### Nodes:
1. **clab-base-02-h1** - Linux host (network-multitool)
2. **clab-base-02-h2** - Linux host (network-multitool)
3. **clab-base-02-sw-h1** - Linux host (network-multitool)
4. **clab-base-02-sw-h2** - Linux host (network-multitool)
5. **clab-base-02-sw1** - Linux switch/host (network-multitool)
6. **clab-base-02-sw2** - Linux switch/host (network-multitool)

All nodes are using the `ghcr.io/hellt/network-multitool:latest` image and are in a **running** state. The lab is using IPv4 addresses in the `172.20.20.0/24` range and IPv6 addresses in the `3fff:172:20:20::/64` range.
```

### Show the network interfaces
Command:
```
python containerlab_agent.py "show me the network interfaces"
```
Output:
```
## Network Interfaces Overview

I found the **base-02** lab running with 6 nodes. Here's a summary of the network interface information:

### Key Observations:

1. **Host Nodes (h1, h2)**: Each has 2 interfaces
   - **eth0**: Management interface (MTU 1500) - connected to Docker network
   - **eth1**: Data interface (MTU 9500) - for inter-node communication

2. **Switch Nodes (sw-h1, sw-h2, sw1, sw2)**: Acting as Linux bridges
   - **eth0**: Management interface (MTU 1500)
   - **br0**: Bridge interface connecting the data plane interfaces
   - **eth1, eth2, eth3**: Data interfaces (MTU 9500) for connections

3. **Interface States**:
   - ✅ Most interfaces are **up** and operational
   - ⚠️ **sw2** has all its data interfaces (br0, eth1, eth2) in **down** state - this might indicate a connectivity issue
   - ⚠️ **sw-h1** has eth3 down
   - ⚠️ **sw-h2** has eth3 down

4. **MTU Settings**:
   - Management interfaces: 1500 bytes
   - Data plane interfaces: 9500 bytes (jumbo frames enabled)
```

### Show how the interfaces are connected
Command:
```
python containerlab_agent.py "show how the network interfaces are connected"
```
Output:
```
Perfect! Now I have all the information. Let me present the network interface connections in a clear format:

## Network Interface Connections - Lab: base-02

Based on the topology, here's how the network interfaces are connected:

### Connection Diagram

```
h1:eth1 ←→ sw-h1:eth1
h2:eth1 ←→ sw-h2:eth1

sw1:eth1 ←→ sw-h1:eth2
sw1:eth2 ←→ sw-h2:eth2

sw2:eth1 ←→ sw-h1:eth3
sw2:eth2 ←→ sw-h2:eth3
```

### Visual Topology

```
        h1                    h2
         │                     │
       eth1                  eth1
         │                     │
       eth1                  eth1
      sw-h1                 sw-h2
     /  │  \               /  │  \
  eth1 eth2 eth3        eth1 eth2 eth3
    │   │   │             │   │   │
    h1  │   │            h2   │   │
        │   │                 │   │
      eth1 eth1             eth2 eth2
        sw1                   sw1
      eth2─────────────────────┘
        │
      eth1                  eth2
        sw2──────────────────┘
```

### Interface Status Summary

**Active Connections (UP):**
- ✅ h1:eth1 ←→ sw-h1:eth1
- ✅ h2:eth1 ←→ sw-h2:eth1
- ✅ sw1:eth1 ←→ sw-h1:eth2
- ✅ sw1:eth2 ←→ sw-h2:eth2

**Inactive Connections (DOWN):**
- ❌ sw2:eth1 ←→ sw-h1:eth3 (both interfaces down)
- ❌ sw2:eth2 ←→ sw-h2:eth3 (both interfaces down)

### Key Observations:

1. **Bridge Switches**: Both `sw-h1` and `sw-h2` have bridge interfaces (br0) configured
2. **MTU Settings**: All point-to-point links use MTU 9500 (jumbo frames enabled)
3. **sw1** is actively connecting sw-h1 and sw-h2 together
4. **sw2** has all its interfaces down, making it inactive in the topology
5. Each host (h1, h2) connects to its corresponding switch (sw-h1, sw-h2)

The topology appears to be a dual-homed setup where two hosts connect to separate access switches, which are then interconnected via sw1 (active) and sw2 (currently down, possibly for redundancy).
```