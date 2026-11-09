"""ASTRA-Sec: NASA/JPL ION-DTN Configuration Generator for 4-Node Space Constellation."""

import os
from typing import Dict, Tuple


class IonNodeConfig:
    """Generates official ION-DTN (.ionconfig, .ionrc, .bprc, .ionsecrc) configuration files."""

    @staticmethod
    def generate_node_config(
        node_num: int,
        node_name: str,
        udp_port: int,
        outduct_targets: Dict[int, Tuple[str, int]],  # next_node_num -> (ip, port)
    ) -> Dict[str, str]:
        """Generates configuration files for an individual ION-DTN node."""
        # 1. .ionconfig
        ionconfig = f"""# ION-DTN Configuration for {node_name} (Node {node_num})
sdrWmSize 50000000
configFlags 1
heapWords 5000000
"""

        # 2. .ionrc
        ionrc = f"""# ION Administration for Node {node_num}
1 {node_num} ''
s
"""

        # 3. .bprc (Bundle Protocol configuration)
        bprc_lines = [
            f"# BPv7 Administration for Node {node_num} ({node_name})",
            "1",
            "a scheme ipn 'ipnfw' 'ipnadminep'",
            f"a endpoint ipn:{node_num}.1 q",
            f"a endpoint ipn:{node_num}.2 q",
            "a protocol udp 1400 100",
            f"a induct udp 127.0.0.1:{udp_port} cli_udp",
        ]
        for target_node, (ip, port) in outduct_targets.items():
            bprc_lines.append(f"a outduct udp {ip}:{port} clo_udp")
        bprc_lines.append("s")
        bprc = "\n".join(bprc_lines) + "\n"

        # 4. .ionsecrc
        ionsecrc = f"""# BPSec Administration for Node {node_num}
1
s
"""

        return {
            f"node{node_num}.ionconfig": ionconfig,
            f"node{node_num}.ionrc": ionrc,
            f"node{node_num}.bprc": bprc,
            f"node{node_num}.ionsecrc": ionsecrc,
        }

    @staticmethod
    def generate_4node_constellation(output_dir: str) -> Dict[str, str]:
        """Generates complete configuration suite for the 4-node ASTRA-Sec space network.

        Node 1: Ground Station A (Port 4556)
        Node 2: Satellite 1 Relay (Port 4557)
        Node 3: Satellite 2 Relay (Port 4558)
        Node 4: Ground Station B (Port 4559)
        """
        os.makedirs(output_dir, exist_ok=True)
        all_files = {}

        # GSA (Node 1) -> sends to SAT1 (Node 2)
        cfg1 = IonNodeConfig.generate_node_config(
            1, "GSA", 4556, {2: ("127.0.0.1", 4557)}
        )
        # SAT1 (Node 2) -> sends to SAT2 (Node 3) and GSA (Node 1)
        cfg2 = IonNodeConfig.generate_node_config(
            2, "SAT1", 4557, {1: ("127.0.0.1", 4556), 3: ("127.0.0.1", 4558)}
        )
        # SAT2 (Node 3) -> sends to GSB (Node 4) and SAT1 (Node 2)
        cfg3 = IonNodeConfig.generate_node_config(
            3, "SAT2", 4558, {2: ("127.0.0.1", 4557), 4: ("127.0.0.1", 4559)}
        )
        # GSB (Node 4) -> sends to SAT2 (Node 3)
        cfg4 = IonNodeConfig.generate_node_config(
            4, "GSB", 4559, {3: ("127.0.0.1", 4558)}
        )

        all_files.update(cfg1)
        all_files.update(cfg2)
        all_files.update(cfg3)
        all_files.update(cfg4)

        for filename, content in all_files.items():
            path = os.path.join(output_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        return all_files
