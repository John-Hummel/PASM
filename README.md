# PASM SDK

Minimal Python SDK for assembling `.asm` source files into raw binary output. Supports both ARM and x86 targets, offering a simple CLI interface for scripting, education, and firmware prototyping.

## ✨ Features

- 🛠 Assemble raw `.asm` files into binary
- 🧠 Supports ARM32 and x86 instruction sets
- 🔧 Command-line interface with `assemble`
- 💡 Scriptable, lightweight, no heavy toolchain
- 🔄 Clean modular structure for integration

## 📦 Installation

```bash
git clone https://github.com/John-Hummel/PASM.git
cd PASM
pip install .
```

## 🚀 Usage

```bash
assemble path/to/your_file.asm -o output.bin
```

By default, `assemble` detects the architecture based on instruction set or flags.

## 📂 Example
Create a file called `add.asm`:

```asm
; Add two numbers (ARM syntax)
MOV r0, #1
MOV r1, #2
ADD r2, r0, r1
```

Then run:

```bash
assemble add.asm -o add.bin
```

## 📁 Folder Structure

```
pasm_sdk/
├── cli.py             # Command-line entry point
├── encode_arm.py      # ARM assembler backend
├── encode_x86.py      # x86 assembler backend
├── instructions.py    # Instruction mappings
├── reader.py          # Input loader and tokenizer
├── __init__.py
examples/
└── add.asm
```

## ⚙️ Supported Architectures

- ✅ ARMv7 / ARM Cortex-M
- ✅ x86 (partial, expanding)

## 📄 License

MIT License — open to all use cases.



**PASM is part of a larger vision to build semantic firmware tooling pipelines. Stay tuned for DSL and reverse tooling integration.**

