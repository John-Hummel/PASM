class Reader:
    def __init__(self):
        self._file = None
        self._line = None
        self._pos = 0
        self._len = 0
        self._line_num = 0
        self._line_pos = 0

    def open(self, filename=None):
        """Open a file for reading."""
        if filename:
            self._file = open(filename, 'r')
        self.read()
        return self

    def close(self):
        """Close the file."""
        if self._file:
            self._file.close()
            self._file = None
        return self

    def read(self):
        """Read the next line from the file."""
        if self._file:
            self._line = self._file.readline()
            if not self._line:
                self._line = None
                return None
            self._len = len(self._line)
            self._line_num += 1
            self._line_pos = 0
            self._pos = 0
        return self

    def get_line(self):
        return self._line

    def get_line_num(self):
        return self._line_num

    def get_line_pos(self):
        return self._line_pos

    def get_pos(self):
        return self._pos

    def get_len(self):
        return self._len

    def get_char(self):
        if self._pos < self._len:
            return self._line[self._pos]
        return None

    def get_next_char(self):
        if self._pos < self._len:
            self._pos += 1
            self._line_pos += 1
            return self._line[self._pos - 1]
        return None

    def get_prev_char(self):
        if self._pos > 0:
            self._pos -= 1
            self._line_pos -= 1
            return self._line[self._pos]
        return None

    def asmparser(self):
        """Reset reader to beginning of the file for another parse pass."""
        if self._file:
            self._file.seek(0)
            self.read()
        return self

    def get_next_instruction(self):
        """Read and return the next parsed instruction line."""
        while self._file:
            line = self._file.readline()
            if not line:
                return None
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if '(' not in line or not line.endswith(')'):
                raise SyntaxError(f"Malformed line: {line}")
            name, arg_str = line.split('(', 1)
            name = name.strip()
            args = arg_str[:-1].strip()
            if args:
                args = [eval(a.strip()) for a in args.split(',')]
            else:
                args = []
            return (name, args)
        return None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
