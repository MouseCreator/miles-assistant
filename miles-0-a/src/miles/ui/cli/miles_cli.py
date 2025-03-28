from typing import Any


class CLIApp:
    _config: Any

    def __init__(self):
        self._config = None

    def mainloop(self):
        while True:
            command = self._prompt()
            if command == "exit":
                print("Exiting...")
                return
            self._execute_command(command)


    def _prompt(self) -> str:
        pass

    def _execute_command(self, command: str):
        pass


def start_cli():
    app = CLIApp()
    app.mainloop()

if __name__ == '__main__':
    start_cli()