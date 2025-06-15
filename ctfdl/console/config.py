class OutputConfig:
    def __init__(self):
        self.quiet = False
        self.verbosity = 1
        self.log_path = None
        self._log_file = None

    def set_log_file(self, path: str):
        self.log_path = path
        self._log_file = open(path, 'a', encoding='utf-8')

    def log(self, message: str):
        if self._log_file:
            self._log_file.write(message + "\n")

output_config = OutputConfig()
