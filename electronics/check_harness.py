"""Checks that both ends of the thigh harness match: hinge-board J1 against thigh-board J3, pin for pin.

The two boards are separate KiCad projects, so nothing else stops their pinouts drifting apart.
Exit status is non-zero on a mismatch. Run after changing either schematic.
"""

import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

KICAD_CLI = os.environ.get('KICAD_CLI', r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe')
BOARDS = (('hinge-board', 'J1'), ('thigh-board', 'J3'))
EXPECTED = {'1': 'VBAT_SW', '2': 'GND', '3': '+3V3', '4': 'SDA', '5': 'SCL', '6': 'FSR_EN', '7': 'FSR_T1', '8': 'FSR_T2'}


def connector_pins(netlist_xml: str, reference: str) -> dict:
    """Maps pin number to net name for one connector in a KiCad XML netlist."""
    pins = {}
    for net in ET.fromstring(netlist_xml).iter('net'):
        for node in net.iter('node'):
            if node.get('ref') == reference:
                pins[node.get('pin')] = net.get('name').lstrip('/')
    return pins


def compare(first: dict, second: dict, expected: dict) -> list:
    """Returns one message per pin that disagrees between the two ends or with the expected pinout."""
    problems = []
    for pin in sorted(set(first) | set(second) | set(expected), key=int):
        a, b, want = first.get(pin), second.get(pin), expected.get(pin)
        if a != b or a != want:
            problems.append(f'pin {pin}: hinge {a}, thigh {b}, expected {want}')
    return problems


def export_netlist(board: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    schematic = os.path.join(here, 'kicad', board, f'{board}.kicad_sch')
    with tempfile.TemporaryDirectory() as temp:
        output = os.path.join(temp, 'netlist.xml')
        subprocess.run([KICAD_CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', output, schematic],
                       check=True, capture_output=True)
        with open(output, encoding='utf-8') as handle:
            return handle.read()


def main() -> int:
    ends = [connector_pins(export_netlist(board), reference) for board, reference in BOARDS]
    problems = compare(ends[0], ends[1], EXPECTED)
    for problem in problems:
        print(problem)
    if not problems:
        print(f'Harness OK: {len(EXPECTED)} pins match on J1 and J3')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
