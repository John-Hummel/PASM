import re
from tkinter import simpledialog, Tk

def setprompt_user(prompt):
    global prompt_user_flag
    prompt_user_flag = prompt
def getprompt_user():
    return prompt_user_flag
prompt_user_flag = True# Default value for prompt_user flag
def encode_mov_arm(line, labels=None, prompt_user=False):
    match = re.match(r"mov\s+r(\d+),\s*#?(\w+)", line, re.IGNORECASE)
    if not match:
        return None
    rd, imm = match.groups()
    rd = int(rd)
    
    if labels and imm in labels:
        imm_val = labels[imm]
    else:
        try:
            imm_val = int(imm, 0)
        except ValueError:
            if prompt_user:
                user_input = input(f"Undefined label or symbol '{imm}' encountered in line: '{line}'. Please provide a value: ")
                try:
                    imm_val = int(user_input, 0)
                except ValueError:
                    print(f"[ERR] Invalid value '{user_input}' for symbol '{imm}'. Defaulting to 0.")
                    imm_val = 0
            else:
                root = Tk()
                root.withdraw()
                user_input = simpledialog.askstring("Missing Value", f"Enter value for symbol '{imm}' in line:\n\n{line}")
                root.destroy()
                if user_input is not None:
                    try:
                        imm_val = int(user_input, 0)
                    except ValueError:
                        print(f"[ERR] Invalid value '{user_input}' for symbol '{imm}'. Defaulting to 0.")
                        imm_val = 0
                else:
                    imm_val = 0

    return (0xE3A00000 | (rd << 12) | imm_val).to_bytes(4, 'little')

def encode_add_arm(line, prompt_user=False):
    match = re.match(r"add\s+r(\d+),\s*r(\d+),\s*#?(\d+)", line, re.IGNORECASE)
    if not match:
        return None
    rd, rn, imm = map(int, match.groups())
    return (0xE2800000 | (rn << 16) | (rd << 12) | imm).to_bytes(4, 'little')

def encode_cmp_arm(line):
    match = re.match(r"cmp\s+r(\d+),\s*#?(\d+)", line, re.IGNORECASE)
    if not match:
        return None
    reg, imm = match.groups()
    reg = int(reg)
    imm = int(imm)
    return bytes([
        imm & 0xFF,
        (reg & 0xF) << 4,
        0x50,
        0xE3
    ])

def encode_b_arm(line, labels=None, current_address=0):
    match = re.match(r"b(eq|ne|gt|lt)?\s+(\w+)", line, re.IGNORECASE)
    if not match or labels is None:
        return None
    cond, label = match.groups()
    cond = cond.lower() if cond else ''
    cond_codes = {'': 0xEA, 'eq': 0x0A, 'ne': 0x1A, 'gt': 0xCA, 'lt': 0xBA}
    if label not in labels:
        return None
    offset = (labels[label] - current_address - 8) >> 2
    if not (-0x800000 <= offset <= 0x7FFFFF):
        return None
    return bytes([
        cond_codes.get(cond, 0xEA),
        (offset >> 16) & 0xFF,
        (offset >> 8) & 0xFF,
        offset & 0xFF
    ])

def encode_bl_arm(line, labels=None, current_address=0):
    match = re.match(r"bl\s+(\w+)", line, re.IGNORECASE)
    if not match or labels is None:
        return None
    label = match.group(1)
    if label not in labels:
        return None
    offset = (labels[label] - current_address - 8) >> 2
    if not (-0x800000 <= offset <= 0x7FFFFF):
        return None
    return bytes([
        0xEB,
        (offset >> 16) & 0xFF,
        (offset >> 8) & 0xFF,
        offset & 0xFF
    ])

def encode_sub_arm(line):
    match = re.match(r"sub\s+r(\d+),\s*r(\d+),\s*#?(\d+)", line, re.IGNORECASE)
    if match:
        rd, rn, imm = map(int, match.groups())
        opcode = 0xE2400000 | (rn << 16) | (rd << 12) | imm
        return opcode.to_bytes(4, 'little')
    match = re.match(r"sub\s+r(\d+),\s*r(\d+),\s*r(\d+)", line, re.IGNORECASE)
    if match:
        rd, rn, rm = map(int, match.groups())
        opcode = 0xE0400000 | (rn << 16) | (rd << 12) | rm
        return opcode.to_bytes(4, 'little')
    return None

def encode_add_arm(line):
    match = re.match(r"add\s+r(\d+),\s*r(\d+),\s*#?(\d+)", line, re.IGNORECASE)
    if match:
        rd, rn, imm = map(int, match.groups())
        opcode = 0xE2800000 | (rn << 16) | (rd << 12) | imm
        return opcode.to_bytes(4, 'little')
    match = re.match(r"add\s+r(\d+),\s*r(\d+),\s*r(\d+)", line, re.IGNORECASE)
    if match:
        rd, rn, rm = map(int, match.groups())
        opcode = 0xE0800000 | (rn << 16) | (rd << 12) | rm
        return opcode.to_bytes(4, 'little')
    return None

def encode_ldr_arm(line):
    match = re.match(r"ldr\s+r(\d+),\s*\[r?(\w+)\](?:,\s*#(\d+))?", line, re.IGNORECASE)
    if not match:
        return None
    rt, rn, offset = match.groups()
    rt = int(rt)

    reg_map = {"sp": 13, "lr": 14, "pc": 15}
    try:
        rn = int(rn)
    except ValueError:
        rn = reg_map.get(rn.lower(), 0)

    offset = int(offset) if offset else 0
    opcode = 0xE5900000 | (rn << 16) | (rt << 12) | offset
    return opcode.to_bytes(4, 'little')


def encode_str_arm(line):
    match = re.match(r"str\s+r(\d+),\s*\[r?(\w+)\](?:,\s*#(\d+))?", line, re.IGNORECASE)
    if not match:
        return None
    rt, rn, offset = match.groups()
    rt = int(rt)

    reg_map = {"sp": 13, "lr": 14, "pc": 15}
    try:
        rn = int(rn)
    except ValueError:
        rn = reg_map.get(rn.lower(), 0)

    offset = int(offset) if offset else 0
    opcode = 0xE5800000 | (rn << 16) | (rt << 12) | offset
    return opcode.to_bytes(4, 'little')


def encode_mul_arm(line):
    match = re.match(r"mul\s+r(\d+),\s*r(\d+),\s*r(\d+)", line, re.IGNORECASE)
    if match:
        rd, rm, rs = map(int, match.groups())
        opcode = 0xE0000090 | (rd << 16) | (rs << 8) | rm
        return opcode.to_bytes(4, 'little')
    return None

def encode_bx_arm(line):
    match = re.match(r"bx\s+r?(\w+)", line, re.IGNORECASE)
    if match:
        reg = match.group(1).lower()
        reg_map = {"lr": 14, "sp": 13, "pc": 15}
        if reg in reg_map:
            rm = reg_map[reg]
        elif reg.isdigit():
            rm = int(reg)
        else:
            rm = 0  # fallback
        return (0xE12FFF10 | rm).to_bytes(4, 'little')
    return None

def encode_push_arm(line):
    match = re.match(r"push\s+\{(.*?)\}", line, re.IGNORECASE)
    if match:
        regs = match.group(1).split(',')
        reg_list = sum([1 << int(r.strip()[1:]) for r in regs if r.strip().startswith('r')])
        opcode = 0xE92D0000 | reg_list
        return opcode.to_bytes(4, 'little')
    return None

def encode_pop_arm(line):
    match = re.match(r"pop\s+\{(.*?)\}", line, re.IGNORECASE)
    if match:
        regs = match.group(1).split(',')
        reg_list = sum([1 << int(r.strip()[1:]) for r in regs if r.strip().startswith('r')])
        opcode = 0xE8BD0000 | reg_list
        return opcode.to_bytes(4, 'little')
    return None

def encode_svc_arm(line):
    match = re.match(r"svc\s+#?(\d+)", line, re.IGNORECASE)
    if match:
        imm = int(match.group(1))
        opcode = 0xEF000000 | (imm & 0xFF)
        return opcode.to_bytes(4, 'little')
    return None
def encode_word_arm(line):
    match = re.match(r"\.word\s+(0x[0-9a-fA-F]+|\d+)", line)
    if match:
        val = int(match.group(1), 0)
        return val.to_bytes(4, 'little')
    return None

def encode_ascii_arm(line):
    match = re.match(r"\.ascii\s+\"(.+?)\"", line)
    if match:
        return match.group(1).encode('ascii')
    return None

def encode_asciz_arm(line):
    match = re.match(r"\.asciz\s+\"(.+?)\"", line)
    if match:
        return match.group(1).encode('ascii') + b'\x00'
    return None

def encode_byte_arm(line):
    match = re.match(r"\.byte\s+(0x[0-9a-fA-F]+|\d+)", line)
    if match:
        val = int(match.group(1), 0)
        return val.to_bytes(1, 'little')
    return None

def encode_zero_fill_arm(line):
    match = re.match(r"\.space\s+(\d+)", line)
    if match:
        size = int(match.group(1))
        return b'\x00' * size
    return None
def encode_half_arm(line):
    if line.startswith('.half'):
        try:
            value = int(line.split()[1], 0)
            return value.to_bytes(2, 'little')
        except Exception as e:
            print(f"[ERR] .half parse failed: {e}")
    return None

def encode_data_arm(line):
    if line.startswith(('.text', '.data', '.global')):
        return b''  # No actual binary output

    return (
        encode_word_arm(line) or
        encode_half_arm(line) or
        encode_byte_arm(line) or
        encode_ascii_arm(line) or
        encode_asciz_arm(line) or
        encode_zero_fill_arm(line)
    )

