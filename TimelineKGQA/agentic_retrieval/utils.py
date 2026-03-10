class DictTree(dict):
    def __missing__(self, key):
        new_val = type(self)()
        self[key] = new_val
        return new_val

    def __add__(self, x):
        if len(self) == 0:
            return 0 + x
        raise ValueError

    def __sub__(self, x):
        if len(self) == 0:
            return 0 - x
        raise ValueError

    def print_hierarchy(self, depth: int = 0):
        indent = " " * (depth * 2)
        for k, v in self.items():
            if isinstance(v, type(self)):
                print(f"{indent}{k}:")
                v.print_hierarchy(depth + 1)
            else:
                print(f"{indent}{k}: {v}")
