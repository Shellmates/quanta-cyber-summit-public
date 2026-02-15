# Operation Desert Storm - Solution


The provided PCAP file (`operation_desert_storm.pcap`) contains mixed network traffic simulating a realistic industrial control system (ICS) environment:

- Background noise (HTTP, DNS, ICMP, simulated Modbus)
- PROFINET real-time packets
- DNP3 traffic over TCP port 20000

Two subtle protocol anomalies hide the two parts of the flag:

1. A **PROFINET** packet misusing an RTA Frame ID with a cyclic-sized payload → hides `{NUC_R0D5`
2. A **DNP3** packet using an unusual File Transfer object (Group 70) → hides `0V3RR1D3}`

## Part 1 – PROFINET Anomaly (RTA misuse)

Step 1: Isolate PROFINET traffic

PROFINET real-time uses EtherType `0x8892`.

  tshark -r operation_desert_storm.pcap -Y "eth.type == 0x8892"

 Step 2: Understand RT vs RTA

RT Cyclic (real-time cyclic): Frame IDs 0x8000 – 0xBFFF, large fixed payloads
RTA (real-time acyclic): Frame IDs 0xC000 – 0xFBFF, typically small payloads

Step 3: Find the RTA misuse
 tshark -r operation_desert_storm.pcap \
  -Y "eth.type == 0x8892 && pn_rt.frame_id >= 0xc000" \
  -T fields -e frame.number -e pn_rt.frame_id -e frame.len 

 Look for the packet with Frame ID in the 0xc000–0xfbff range (usually 0xc003) but with large payload length.

Step 4: Extract the hidden data
 tshark -r operation_desert_storm.pcap \
  -Y "frame.number == (ur frame number)" \
  -x

## Part 2 – DNP3 Anomaly (File Transfer abuse) 
 Step 1: Isolate DNP3 traffic
  tshark -r operation_desert_storm.pcap -Y "tcp.port == 20000"

Step 2: Look for unusual objects
  tshark -r operation_desert_storm.pcap \
  -Y "tcp.port == 20000 && frame contains 46:03" \
  -T fields -e frame.number

Step 3: Extract the hidden data
  tshark -r operation_desert_storm.pcap \
  -Y "tcp.port == 20000 && frame contains 46:03" \
  -T fields -e data | xxd -r -p | strings

**Flag:** shellmates{NUC_R0D5_0V3RR1D3}
