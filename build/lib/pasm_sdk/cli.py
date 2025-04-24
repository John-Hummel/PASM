import argparse
from instructions import Assembler

def handle_file(input_path: str, output_path: str = None, hex: bool = False):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    assembler = Assembler()
    print(f"[+] Reading file: {input_path}")

    label_map = assembler.resolve_labels_regex(raw_text)
    print(f"[+] Labels: {label_map}")
    label_map = assembler.auto_define_missing_labels(raw_text, label_map)

    arch = assembler.detect_architecture(assembler.parse_instructions(raw_text))
    print(f"[+] Architecture detected: {arch}")

    binary = assembler.assemble(raw_text)

    if output_path and not hex:
        with open(output_path, "wb") as f:
            f.write(binary)
    elif output_path and hex:
        with open(output_path, "w") as f:
            binarytohex = " ".join(f"{byte:02X}" for byte in binary)
            f.write(binarytohex)
        print(f"[OK] Assembled: {input_path} -> {output_path} ({len(binary)} bytes)")
    else:
        print(f"[+] Binary size: {len(binary)} bytes (no output file specified)")

def main():
    parser = argparse.ArgumentParser(description="pasm CLI - Minimal Assembler for ARM/x86")
    parser.add_argument("file", help="Path to the .asm source file")
    parser.add_argument("--output", help="Output binary file path")
    parser.add_argument("--hex", action="store_true", help="Output instructions as hex")
    args = parser.parse_args()

    handle_file(args.file, args.output, args.hex)

if __name__ == "__main__":
    main()
