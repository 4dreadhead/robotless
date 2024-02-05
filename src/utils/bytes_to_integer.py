class BytesToInteger(bytes):
    def __getitem__(self, key):
        result = super().__getitem__(key)
        return BytesToInteger(result) if isinstance(key, slice) else result

    @property
    def to_i(self):
        return int.from_bytes(self, byteorder="big")

    def take(self, count):
        return self[:count].to_i, self[count:]
