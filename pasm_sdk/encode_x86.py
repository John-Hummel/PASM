import re

def encode_mov_reg_imm(line):
    match = re.match(r"mov\s+([re]?[a-d]x|[re][bs]p|[re][sd]i),\s*(\d+|0x[0-9a-fA-F]+)", line, re.IGNORECASE)
    if not match:
        return None
    reg, imm = match.groups()
    reg = reg.lower()
    imm_val = int(imm, 0)
    register_encoding = {
        'eax': 0xB8, 'ecx': 0xB9, 'edx': 0xBA, 'ebx': 0xBB,
        'esp': 0xBC, 'ebp': 0xBD, 'esi': 0xBE, 'edi': 0xBF,
        'rax': 0x48, 'rcx': 0x48, 'rdx': 0x48, 'rbx': 0x48,
    }
    if reg not in register_encoding:
        return None
    if reg.startswith('r'):
        base = {
            'rax': b'\xB8', 'rcx': b'\xB9', 'rdx': b'\xBA', 'rbx': b'\xBB'
        }
        return b'\x48' + base.get(reg, b'') + imm_val.to_bytes(4, 'little')
    opcode = register_encoding[reg]
    return bytes([opcode]) + imm_val.to_bytes(4, 'little')

def encode_mov_reg_symbol(line):
    match = re.match(r"mov\s+(e?[a-d]x|[er]di|[er]si|[er]bp|[er]sp),\s*[^,]+", line, re.IGNORECASE)
    if match:
        reg = match.group(1).lower()
        reg_op = {
            'ecx': b'\xB9', 'edx': b'\xBA', 'ebx': b'\xBB', 'edi': b'\xBF', 'esi': b'\xBE',
            'rdi': b'\x48\xBF', 'rsi': b'\x48\xBE'
        }
        return reg_op.get(reg, b'\x90') + (b'\x00' * (8 if reg.startswith('r') else 4))
    return None

def encode_alu_imm(line):
    match = re.match(r"(add|or)\s+(e?[a-d]x|eax|ebx|ecx|edx|esp),\s*(\d+|0x[0-9a-fA-F]+)", line, re.IGNORECASE)
    if not match:
        return None
    op, reg, imm = match.groups()
    reg = reg.lower()
    imm = int(imm, 0)
    alu_opcodes = {'add': {'eax': b'\x05'}, 'or': {'eax': b'\x0D'}}
    if reg == 'eax' and op in alu_opcodes:
        return alu_opcodes[op][reg] + imm.to_bytes(4, 'little')
    return None

def encode_xor_reg_reg(line):
    match = re.match(r"xor\s+([re]?[a-d]x|rdi),\s*\1", line, re.IGNORECASE)
    if match:
        reg = match.group(1).lower()
        xor_map = {
            'eax': b'\x31\xc0', 'ebx': b'\x31\xdb', 'ecx': b'\x31\xc9', 'edx': b'\x31\xd2',
            'rax': b'\x48\x31\xc0', 'rbx': b'\x48\x31\xdb', 'rdi': b'\x48\x31\xff'
        }
        return xor_map.get(reg, None)
    return None

def encode_syscall(line):
    if re.match(r"int\s+0x80", line, re.IGNORECASE):
        return b'\xCD\x80'
    elif line.strip() == 'syscall':
        return b'\x0F\x05'
    return None

def encode_nop(line):
    if line.strip() == 'nop':
        return b'\x90'
    return None

def encode_stub(line):
    return b'\x90'
