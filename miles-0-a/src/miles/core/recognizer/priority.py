from typing import Dict

from src.miles.core.matcher.matcher import ConnectionType, MatchConnection


# higher priority = choose path first
# expected ranges:
# - MATCHING 0+
# - WORD 500+
# - AUTOMATIC 1000+

class PriorityManager:
    _store: Dict[str, int]

    def __init__(self, def_automatic=1000, def_word=500, def_matching=0):
        self._store = {}
        self._def_automatic = def_automatic
        self._def_word = def_word
        self._def_matching = def_matching

    def _format_key(self, plugin: str, p_type: ConnectionType, argument: str):
        p_type_str = p_type.name
        return "|".join([plugin, p_type_str, argument])

    def get_priority(self, c: MatchConnection) -> int:
        key = self._format_key(c.plugin, c.connection_type, c.connection_arg)
        value = self._store.get(key, None)
        if value is not None:
            return value

        if c.connection_type == ConnectionType.WORD:
            return self._def_word
        if c.connection_type == ConnectionType.AUTOMATIC:
            return self._def_automatic
        if c.connection_type == ConnectionType.MATCHING:
            return self._def_matching
        raise ValueError(f'Unknown connection type: {c.connection_type}')

    def has_priority(self, plugin:str, p_type: ConnectionType, argument: str) -> bool:
        key = self._format_key(plugin, p_type, argument)
        return key in self._store.keys()

    def set_priority(self, plugin: str, p_type: ConnectionType, argument: str, priority: int) -> None:
        key = self._format_key(plugin, p_type, argument)
        self._store[key] = priority

