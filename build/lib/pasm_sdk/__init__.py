from .instructions import InstructionDictionary, Assembler
from .reader import Reader
from .encode_x86 import (
    encode_mov_reg_imm, encode_mov_reg_symbol, encode_alu_imm,
    encode_xor_reg_reg, encode_syscall, encode_nop
)
from .encode_arm import encode_mov_arm, encode_add_arm, encode_svc_arm

__all__ = [
    "Assembler",
    "InstructionDictionary",
    "encode_mov_arm",
    "encode_add_arm",
    "encode_svc_arm",
    "encode_mov_reg_imm",
    "encode_mov_reg_symbol",
    "encode_alu_imm",
    "encode_xor_reg_reg",
    "encode_syscall",
    "encode_nop",
    "Reader",
    "InstructionDictionary.x86",
    "InstructionDictionary.arm",
]
