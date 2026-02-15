# Silent Whispers — Solution Write-up

## 🧠 Overview

This challenge hides a flag using a **covert TCP channel**.  
The payloads themselves do not contain the flag — instead, the secret is encoded in the **differences between TCP sequence numbers**.

The PCAP also contains:  
- Multiple protocols (UDP, ICMP, ARP)  
- TCP noise packets  
- Out-of-order packet capture

The goal is to **reconstruct the logical TCP stream** and extract the hidden message.

---

## 🔍 Step 1 — Identify the Relevant Traffic

By inspecting the PCAP, we observe a TCP flow with a high number of packets between:

- Source IP: `10.10.10.5`  
- Destination IP: `10.10.20.7`  
- Source port: `51514`  
- Destination port: `44444`  

This flow stands out due to:  
- High packet count  
- Minimal payload data  
- Unusual sequence number behavior  

All other protocols and TCP streams are noise.

---

## 🔎 Step 2 — Filter the TCP Stream

Using Wireshark or Scapy, we isolate the relevant TCP packets.

**Example Wireshark display filter:**

tcp.srcport == 51514 && tcp.dstport == 44444


**Or programmatically using Scapy:**

```python
from scapy.all import *

pkts = rdpcap("silent_whispers_realistic_hard.pcap")

flow = [
    p for p in pkts
    if TCP in p
    and p[TCP].sport == 51514
    and p[TCP].dport == 44444
]
🔄 Step 3 — Reorder Packets by Sequence Number
The packet order in the PCAP does not represent the logical TCP order.
TCP sequence numbers must be used instead.

flow_sorted = sorted(flow, key=lambda p: p[TCP].seq)
This reconstructs the logical data stream.

🔢 Step 4 — Extract Sequence Number Differences
We now compute the difference between consecutive TCP sequence numbers.

seqs = [p[TCP].seq for p in flow_sorted]

diffs = []
for i in range(1, len(seqs)):
    diffs.append(seqs[i] - seqs[i - 1])
Most differences are noise, but some values fall within the printable ASCII range.

🔓 Step 5 — Decode the Flag
Printable ASCII characters are in the range 32–126.
We convert valid differences into characters.

flag = ""

for d in diffs:
    if 32 <= d <= 126:
        flag += chr(d)

print(flag)