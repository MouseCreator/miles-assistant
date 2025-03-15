from enum import Enum
from typing import Self, List

from src.miles.core.command.command import WordComponent, ComponentVisitor, NamedComponent, \
    ChoiceComponent, ListComponent, OptionalComponent, MatchingComponent, SequenceComponent, RootComponent
from src.miles.core.matcher.comand_defintion import CommandDefinition, CommandNamespace
from src.miles.core.matcher.command_pool import CommandPool
from src.miles.core.matcher.matcher_error import MatcherError
from src.miles.utils.list_utils import index_of
from src.miles.utils.pretty import PrintableStructure
from src.miles.utils.strings import print_list


class ConnectionType(Enum):
    AUTOMATIC = 0
    WORD = 1
    MATCHING = 2


class MatchConnection(PrintableStructure):
    def __init__(self, connection_type: ConnectionType, plugin: str | None, connection_arg: str | None):
        self.connection_type = connection_type
        self.plugin = plugin
        self.connection_arg = connection_arg

    def __str__(self):
        return f"MatchConnection {{ {self.connection_type.name}, {self.plugin}, {self.connection_arg} }}"


    def __eq__(self, other):
        if not isinstance(other, MatchConnection):
            return False
        return (self.plugin == other.plugin
                and self.connection_type == other.connection_type
                and self.connection_arg == other.connection_arg)

    def sprint(self):
        result = '(' + self.connection_type.name
        if self.plugin:
            result += ', '
            result += self.plugin
        if self.connection_arg:
            result += ', '
            result += self.connection_arg
        result += ')'
        return result

class MatchState:
    _state_id: int
    _connections: List[MatchConnection]
    _destinations: List[Self]
    _priorities: List[int]
    _final: bool

    def __hash__(self):
        return self._state_id

    def __init__(self, state_id: int, is_final: bool = False):
        self._state_id = state_id
        self._connections = []
        self._destinations = []
        self._priorities = []
        self._final = is_final

    def __str__(self):
        return (f"State {{ id={self._state_id}, "
                f"connections={print_list(self._connections)}, "
                f"destinations={print_list([t._state_id for t in self._destinations])}, "
                f"priorities={print_list(self._priorities)}}}")

    @classmethod
    def initial(cls) -> Self:
        return MatchState(0)

    def __eq__(self, other):
        if not isinstance(other, MatchState):
            return False
        return self._state_id == other._state_id

    def has_connection(self, connection: MatchConnection, priority: int | None=None):
        index = index_of(self._connections, connection)
        if index == -1:
            return False
        if priority is None:
            return True
        return self._priorities[index] == priority

    def get_destination(self, connection):
        index = index_of(self._connections, connection)
        if index < 0:
            return None
        return self._destinations[index]

    def get_priority(self, connection: MatchConnection):
        index = index_of(self._connections, connection)
        if index < 0:
            return None
        return self._priorities[index]
    def all_connections(self) -> List[MatchConnection]:
        return list(self._connections)

    def update_priority(self, connection: MatchConnection, priority: int):
        index = index_of(self._connections, connection)
        if index == -1:
            return None

        if self._priorities[index] < priority:
            self._priorities[index] = priority
        return self._destinations[index]

    def add_connection(self, connection: MatchConnection, priority:int, new_state: Self):
        if self.has_connection(connection):
            raise MatcherError(f'Cannot add connection, because one already exists: {connection}')
        self._connections.append(connection)
        self._priorities.append(priority)
        self._destinations.append(new_state)
        return new_state
    def is_final(self):
        return self._final


class Matcher:
    def __init__(self, states : None | List[MatchState] = None):
        if states is None or len(states) == 0:
            self._initial_state = MatchState.initial()
            self._all_states = [self._initial_state]
        else:
            self._initial_state = states[0]
            self._all_states = list(states)

    def get_initial_state(self) -> MatchState:
        return self._initial_state




class MatcherFactory:

    def __init__(self, pool: CommandPool):
        self._pool = pool
        self._initial = MatchState.initial()
        self._state_index_count = 0
        self._matcher = None
        self._all_states = [self._initial]
        self._automatic_priority = 0

    def _create_empty_state(self, final: bool = False):
        self._state_index_count += 1
        new_state = MatchState(self._state_index_count, is_final=final)
        self._all_states.append(new_state)
        return new_state


    def _move_and_add_word(self, state: MatchState, plugin: str, word_component: WordComponent) -> MatchState:
        connection = MatchConnection(ConnectionType.WORD, plugin, word_component.get_content())
        if state.has_connection(connection, word_component.get_priority()):
            return state.update_priority(connection, word_component.get_priority())
        new_state = self._create_empty_state()
        return state.add_connection(connection, word_component.get_priority(), new_state)

    def _move_and_add_matching(self, state: MatchState, plugin: str, matching_component: MatchingComponent) -> MatchState:
        connection = MatchConnection(ConnectionType.MATCHING, plugin, matching_component.get_content())
        if state.has_connection(connection, matching_component.get_priority()):
            return state.update_priority(connection, matching_component.get_priority())
        new_state = self._create_empty_state()
        return state.add_connection(connection, matching_component.get_priority(), new_state)
    def _move_automatically(self, move_from: MatchState, move_to: MatchState, plugin: str, label: str):
        if move_from is None or move_to is None:
            return
        connection = MatchConnection(ConnectionType.AUTOMATIC, plugin, label)
        if move_from.has_connection(connection):
            return move_to
        move_from.add_connection(connection, self._automatic_priority, move_to)

    def _append_command_signature(self, command_def: CommandDefinition, from_state: MatchState):
        command = command_def.get_command()

        class SignatureVisitor(ComponentVisitor):

            initial_state: MatchState
            previous_state_buffer: MatchState
            namespace: CommandNamespace
            parent: MatcherFactory

            def __init__(self, initial_state : MatchState, namespace: CommandNamespace, parent: MatcherFactory):
                self.initial_state = initial_state
                self.previous_state_buffer = initial_state
                self.namespace = namespace
                self.parent = parent


            def _format_namespace(self):
                result = ''
                if self.namespace.plugin_name:
                    result += self.namespace.plugin_name
                result += '|'
                if self.namespace.namespace_name:
                    result += self.namespace.namespace_name
                result += '|'
                if self.namespace.command_name:
                    result += self.namespace.command_name

                return result

            def _new_state(self):
                return self.parent._create_empty_state()
            def _plugin(self):
                return self.namespace.plugin_name

            def visit_root(self, root: RootComponent):
                root.get_content().accept_visitor(self)
                prev = self.previous_state_buffer
                final_state = self.parent._create_empty_state(final=True)
                label = 'recognize ' + self._format_namespace()
                self.parent._move_automatically(prev, final_state, self._plugin(), label)
                self.previous_state_buffer = final_state

            def visit_sequence(self, sequence: SequenceComponent):
                content = sequence.get_content()
                for elem in content:
                    elem.accept_visitor(self)


            def visit_word(self, word: WordComponent):
                prev = self.previous_state_buffer
                moved_to = self.parent._move_and_add_word(prev, self._plugin(), word)
                self.previous_state_buffer = moved_to


            def visit_matching(self, matching: MatchingComponent):
                matching_name = matching.get_content()

                prev = self.previous_state_buffer
                begins_at = self._new_state()
                self.parent._move_automatically(prev, begins_at, self._plugin(), f'begin matching {matching_name}')
                self.previous_state_buffer = begins_at

                moved_to = self.parent._move_and_add_matching(prev, self._plugin(), matching)

                ends_at = self._new_state()
                self.parent._move_automatically(moved_to, ends_at, self._plugin(), f'end matching {matching_name}')
                self.previous_state_buffer = ends_at

            def visit_optional(self, optional: OptionalComponent):
                prev = self.previous_state_buffer
                begins_at = self._new_state()
                ends_at = self._new_state()

                self.parent._move_automatically(prev, ends_at, self._plugin(), 'skip optional')
                self.parent._move_automatically(prev, begins_at, self._plugin(), 'begin optional')

                self.previous_state_buffer = begins_at

                content = optional.get_content()
                content.accept_visitor(self)
                after_optional = self.previous_state_buffer
                self.parent._move_automatically(after_optional, ends_at, self._plugin(), 'end optional')

                self.previous_state_buffer = ends_at


            def visit_list(self, lst: ListComponent):
                prev = self.previous_state_buffer
                begins_at = self._new_state()
                self.parent._move_automatically(prev, begins_at, self._plugin(), 'begin list')
                self.previous_state_buffer = begins_at

                content = lst.get_content()
                content.accept_visitor(self)
                after_list = self.previous_state_buffer
                ends_at = self._new_state()

                self.parent._move_automatically(after_list, begins_at, self._plugin(), 'repeat list')
                self.parent._move_automatically(after_list, ends_at, self._plugin(), 'end list')

            def visit_choice(self, choice: ChoiceComponent):
                prev = self.previous_state_buffer
                begins_at = self._new_state()
                self.parent._move_automatically(prev, begins_at, self._plugin(), 'begin choice')
                self.previous_state_buffer = begins_at

                content = choice.get_content()
                end_state = self._new_state()
                for component in content:
                    self.previous_state_buffer = begins_at
                    component.accept_visitor(self)
                    component_ends = self.previous_state_buffer

                    # join all choices to the empty state at the end
                    self.parent._move_automatically(component_ends, end_state, self.namespace.plugin_name, 'end choice')
                self.previous_state_buffer = end_state

            def visit_named(self, named: NamedComponent):
                name = named.get_name()
                prev = self.previous_state_buffer
                begins_at = self._new_state()
                self.parent._move_automatically(prev, begins_at, self.namespace.plugin_name, f'begin name {name}')
                self.previous_state_buffer = begins_at

                named.get_content().accept_visitor(self)

                after_named = self.previous_state_buffer
                ends_at = self._new_state()

                self.parent._move_automatically(after_named, ends_at, self.namespace.plugin_name, f'end name {name}')

        sig = SignatureVisitor(from_state, command_def.get_namespace(), self)
        command.accept_visitor(sig)

    def _format_namespace(self, namespace: CommandNamespace) -> str:
        return f'{namespace.plugin_name}|{namespace.namespace_name}'

    def _append_namespace(self, command_def: CommandDefinition, from_state :MatchState):
        state = from_state
        namespace = command_def.get_namespace()
        arguments = namespace.get_arguments()
        if not arguments:
            return from_state
        plugin = namespace.plugin_name
        for arg in arguments:
            state = self._move_and_add_word(state, plugin, arg)
        return state

    def _append_namespace_and_command(self, command_def: CommandDefinition, from_state : MatchState):
        state = self._append_namespace(command_def, from_state)
        self._append_command_signature(command_def, state)

    def _process_definition(self, command_def: CommandDefinition):
        self._append_namespace_and_command(command_def, self._initial)
        self._append_command_signature(command_def, self._initial)


    def create(self) -> Matcher:
        if self._matcher is None:
            for command_definition in self._pool:
                self._process_definition(command_definition)
            self._matcher = Matcher(self._all_states)
        return self._matcher







