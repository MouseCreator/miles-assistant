
class CommandDefinitionContext:
    pass

class CommandDefinition:
    def __init__(self, namespace, command, on_match):
        self._namespace = namespace
        self._command = command
        self._on_match = on_match
    def get_namespace(self):
        return self._namespace
    def get_command(self) -> str:
        return self._command
    def on_match(self, context : CommandDefinitionContext):
        self._on_match(context)