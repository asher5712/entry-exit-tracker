class Echo:
    """An object with a write() method for csv.writer to call."""
    def write(self, value):
        return value
