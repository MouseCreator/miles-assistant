

class SharedNode:

    def __init__(self, connection_type: str, argument: str, name: str):
        self.connection_type = connection_type
        self.argument = argument
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, SharedNode):
            return False
        return (
                self.connection_type == other.connection_type
                and
                self.argument == other.argument
                and
                self.name == other.name
                )