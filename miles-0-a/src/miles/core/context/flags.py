from typing import TypeVar, Any, Optional, Type, Dict, Self

T = TypeVar('T')

class Flags:
    _flags: Dict[str, Any]
    def set_flag(self, name: str, value: Any):
        self._flags[name] = value

    def get_flag(self, name: str, type_to_cast: Optional[Type[T]] = None) -> T | None:
        value = self._flags.get(name, None)
        if value is None:
            return None
        if type_to_cast is None or type_to_cast is Any:
            return value
        try:
            if type_to_cast is bool:
                return str(value).lower() in ('true', '1')
            return type_to_cast(value)
        except (ValueError, TypeError):
            return None
    def has_flag(self, name: str) -> bool:
        return name in self._flags

    def copy(self) -> Self:
        flags = Flags()
        flags._flags = self._flags.copy()
        return flags



