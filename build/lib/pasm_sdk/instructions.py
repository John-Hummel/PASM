import re
from reader import Reader 
from typing import List, Tuple, Dict

# Default value for prompt_user flag
class InstructionDictionary:
    @staticmethod
    def x86():
        return {
            'Registers': {
                '64-bit': ['RAX', 'RBX', 'RCX', 'RDX', 'RSI', 'RDI', 'RBP', 'RSP', 'R8-R15'],
                '32-bit': ['EAX', 'EBX', 'ECX', 'EDX', 'ESI', 'EDI', 'EBP', 'ESP', 'R8D-R15D'],
                '16-bit': ['AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP', 'R8W-R15W'],
                '8-bit': ['AL', 'BL', 'CL', 'DL', 'SIL', 'DIL', 'BPL', 'SPL', 'R8B-R15B']
            },
            'Syscall Convention (Linux)': {
                'RAX': 'Syscall number',
                'RDI': '1st argument',
                'RSI': '2nd argument',
                'RDX': '3rd argument',
                'R10': '4th argument',
                'R8': '5th argument',
                'R9': '6th argument'
            },
            'System V Calling Convention (Function Args)': {
                'RDI': 'Arg 1',
                'RSI': 'Arg 2',
                'RDX': 'Arg 3',
                'RCX': 'Arg 4',
                'R8': 'Arg 5',
                'R9': 'Arg 6',
                'RAX': 'Return value'
            },
            'Data Directives': {
                'db': 'Define byte',
                'dw': 'Define word (16-bit)',
                'dd': 'Define double word (32-bit)',
                'dq': 'Define quad word (64-bit)'
            },
            'Arithmetic and Logic': {
                'mov': 'Move data',
                'add': 'Addition',
                'sub': 'Subtraction',
                'imul': 'Signed multiplication',
                'idiv': 'Signed division',
                'inc': 'Increment',
                'dec': 'Decrement',
                'and': 'Bitwise AND',
                'or': 'Bitwise OR',
                'xor': 'Bitwise XOR',
                'not': 'Bitwise NOT',
                'shl': 'Shift left',
                'shr': 'Shift right'
            },
            'Control Flow': {
                'jmp': 'Unconditional jump',
                'call': 'Function call',
                'ret': 'Return from function',
                'cmp': 'Compare',
                'je/jz': 'Jump if equal / zero',
                'jne/jnz': 'Jump if not equal / not zero',
                'jg': 'Jump if greater',
                'jl': 'Jump if less',
                'ja': 'Jump if above (unsigned)',
                'jb': 'Jump if below (unsigned)'
            },
            'Syscall Example': [
                'mov rax, 60 ; syscall: exit',
                'xor rdi, rdi ; status 0',
                'syscall'
            ],
            'Memory Access Syntax': {
                '[rax]': 'Access memory at address in RAX',
                '[rsi + 8]': 'Access memory at RSI + 8',
                'qword [rbx]': 'Access 64-bit value at address in RBX'
            }
        }

    @staticmethod
    def arm():
        return {

        'Registers': {
            'General': ['r0' , 'r1' , 'r2' , 'r3' , 'r4' , 'r5' , 'r6' , 'r7' ,
                        'r8' , 'r9' , 'r10', 'r11', 'r12', 'sp', 'lr', 'pc']
        },
        'Syscall Convention (Linux)': {
            'r7': 'Syscall number',
            'r0': 'Arg 1 / Return',
            'r1': 'Arg 2',
            'r2': 'Arg 3',
            'r3': 'Arg 4',
            'r4': 'Arg 5',
            'r5': 'Arg 6'
        },
        'Arithmetic and Logic': {
            'mov': 'Move immediate or register',
            'add': 'Add register or immediate',
            'sub': 'Subtract register or immediate',
            'mul': 'Multiply registers',
            'cmp': 'Compare registers or register/immediate'
        },
        'Control Flow': {
            'b': 'Unconditional branch',
            'beq': 'Branch if equal',
            'bne': 'Branch if not equal',
            'bgt': 'Branch if greater than',
            'blt': 'Branch if less than',
            'bl': 'Branch with link (function call)',
            'bx': 'Branch to register (usually `bx lr`)'
        },
        'Memory Access': {
            'ldr': 'Load word from memory',
            'str': 'Store word to memory'
        },
        'Stack Operations': {
            'push': 'Push registers to stack',
            'pop': 'Pop registers from stack'
        },
        'System': {
            'svc': 'Supervisor call (syscall)'
        },
        'Data Directives': {
            '.word': 'Define 4-byte constant',
            '.half': 'Define 2-byte constant',
            '.byte': 'Define 1-byte constant',
            '.ascii': 'Define string (no null)',
            '.asciz': 'Define string (null-terminated)',
            '.space': 'Reserve zeroed bytes'
        }
    }

        



class Assembler:
    def __init__(self):
        self.reader = Reader()

    def resolve_labels_regex(self, raw_text: str) -> Dict[str, int]:
        lines = raw_text.splitlines()
        labels = {}
        addr = 0
        for line in lines:
            match = re.match(r'^\s*(\w+):\s*(.*?)\s*$', line)
            if match:
                label, trailing = match.groups()
                labels[label] = addr
                if trailing:
                    addr += 4
            elif line.strip() and not line.strip().endswith(':'):
                addr += 4
        return labels



    def parse_instructions(self,raw_text: str) -> List[Tuple[int, str]]:
        def expand_rept(lines: List[str]) -> List[str]:
            result = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                rept_match = re.match(r'\.rept\s+(\d+)', line, re.IGNORECASE)
                if rept_match:
                    count = int(rept_match.group(1))
                    block = []
                    i += 1
                    depth = 1
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if re.match(r'\.rept\s+\d+', sub_line, re.IGNORECASE):
                            depth += 1
                        elif sub_line.lower() == '.endr':
                            depth -= 1
                            if depth == 0:
                                break
                        block.append(lines[i])
                        i += 1
                    result.extend(expand_rept(block) * count)
                    i += 1  # skip .endr
                else:
                    result.append(lines[i])
                    i += 1
            return result

        lines = raw_text.splitlines()
        expanded_lines = expand_rept(lines)

        parsed = []
        addr = 0
        for line in expanded_lines:
            line = line.strip()
            if not line or line.endswith(':'):
                continue
            match = re.match(r'^\s*(\w+):\s*(.*?)\s*$', line)
            if match:
                _, trailing = match.groups()
                if trailing:
                    parsed.append((addr, trailing.strip()))
                    addr += 4
            else:
                parsed.append((addr, line))
                addr += 4
        return parsed

    def auto_define_missing_labels(self,lines, label_map):
        used_labels = set()
        label_usage_pattern = re.compile(r'\b(?:b(?:ne|eq|gt|lt)?|bl)\s+(\w+)', re.IGNORECASE)
        
        address = 0
        label_assignments = {}
        for line in lines:
            match = label_usage_pattern.search(line)
            if match:
                label = match.group(1)
                if label not in label_map:
                    label_assignments[label] = address + 8  # branch skips one instr
            if line.strip() and not line.strip().endswith(':'):
                address += 4

        # Assign safe fallback positions
        label_map.update(label_assignments)
        return label_map

    def assemble(self, raw_text: str) -> bytearray:
        label_map = self.resolve_labels_regex(raw_text)
        parsed = self.parse_instructions(raw_text)
        arch = self.detect_architecture(parsed)

        max_addr = parsed[-1][0] + 4
        binary = bytearray(max_addr)

        for addr, line in parsed:
            code = line.split(';')[0].strip()
            if not code:
                continue

            print(f"[+] Encoding instruction: {code} @ {addr:#04x} (Arch: {arch})")
            encoded = self._encode_instruction(code.lower(), arch, label_map, current_address=addr)

            if encoded:
                binary[addr:addr + len(encoded)] = encoded
                print("    [BYTES]", " ".join(f"{b:02x}" for b in encoded))
            elif not code.startswith(('.text', '.data', '.global')):
                print(f"[ERR] Unrecognized or unhandled: {code}")
                binary[addr:addr + 1] = self.encode_stub(code)
                print("    [FALLBACK]", self.encode_stub(code).hex())

        print(f"[=] Final binary length: {len(binary)} bytes")
        return binary

    def _encode_instruction(self, line, arch, label_map, current_address):
        if arch == "x86":
            from encode_x86 import (
                encode_mov_reg_imm, encode_mov_reg_symbol, encode_alu_imm,
                encode_xor_reg_reg, encode_syscall, encode_nop
            )
            return (
                encode_mov_reg_imm(line) or
                encode_mov_reg_symbol(line) or
                encode_alu_imm(line) or
                encode_xor_reg_reg(line) or
                encode_syscall(line) or
                encode_nop(line)
            )
        elif arch == "arm":
            if line.startswith(('.text', '.data', '.global')):
                return b''  # No actual binary output

            from encode_arm import (
                encode_mov_arm, encode_add_arm, encode_svc_arm, encode_cmp_arm,
                encode_b_arm, encode_sub_arm, encode_ldr_arm, encode_str_arm,
                encode_bx_arm, encode_push_arm, encode_mul_arm, encode_pop_arm,
                encode_data_arm, encode_bl_arm
            )
            return (
                encode_mov_arm(line, labels=label_map) or
                encode_add_arm(line) or
                encode_svc_arm(line) or
                encode_cmp_arm(line) or
                encode_b_arm(line, labels=label_map, current_address=current_address) or
                encode_sub_arm(line) or
                encode_ldr_arm(line) or
                encode_str_arm(line) or
                encode_bx_arm(line) or
                encode_push_arm(line) or
                encode_mul_arm(line) or
                encode_pop_arm(line) or
                encode_data_arm(line) or
                encode_bl_arm(line, labels=label_map, current_address=current_address)
            )
        return None

    def detect_architecture(self, parsed: List[Tuple[int, str]]) -> str:
        x86_score = sum(1 for _, l in parsed if any(x in l.lower() for x in ["rax", "eax", "syscall", "int 0x80", "ebx", "ecx"]))
        arm_score = sum(1 for _, l in parsed if any(x in l.lower() for x in ["r0", "r1", "svc", "mov r", "add r", "r7"]))
        return "arm" if arm_score > x86_score else "x86"

    @staticmethod
    def encode_stub(line: str) -> bytes:
        return b'\x90'  # NOP (or use b'\x00' for ARM filler)