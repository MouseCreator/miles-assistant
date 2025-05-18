from src.miles.core.command.command import WordComponent, ComponentVisitor, NamedComponent, \
    ChoiceComponent, ListComponent, OptionalComponent, MatchingComponent, SequenceComponent, RootComponent, Command
from src.miles.core.matcher.comand_defintion import CommandNamespace
from src.miles.core.matcher.matcher import Matcher, MatchState, MatchConnection, ConnectionType


class MatcherFactory:

    def __init__(self):
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

    def _move_and_add_word(self,
                           state: MatchState,
                           word_component: WordComponent,
                           name: str | None) -> MatchState:
        connection = MatchConnection(ConnectionType.WORD, word_component.get_content(), name)
        if state.has_connection(connection, word_component.get_priority()):
            return state.update_priority(connection, word_component.get_priority())
        new_state = self._create_empty_state()
        return state.add_connection(connection, word_component.get_priority(), new_state)

    def _move_and_add_matching(self,
                               state: MatchState,
                               matching_component: MatchingComponent,
                               name: str | None) -> MatchState:
        connection = MatchConnection(ConnectionType.MATCHING, matching_component.get_content(), name)
        if state.has_connection(connection, matching_component.get_priority()):
            return state.update_priority(connection, matching_component.get_priority())
        new_state = self._create_empty_state()
        return state.add_connection(connection, matching_component.get_priority(), new_state)

    def _move_automatically(self,
                            move_from: MatchState,
                            move_to: MatchState | None,
                            label: str, name: str | None) -> MatchState:
        connection = MatchConnection(ConnectionType.AUTOMATIC, label, name)
        if move_from.has_connection(connection):
            return move_from.get_destination(connection)

        if move_to is None:
            move_to = self._create_empty_state()

        return move_from.add_connection(connection, self._automatic_priority, move_to)

    def _append_command_signature(self, command: Command, c_name: str, from_state: MatchState):
        class SignatureVisitor(ComponentVisitor):

            initial_state: MatchState
            previous_state_buffer: MatchState
            parent: MatcherFactory
            command_name: str

            def __init__(self, initial_state: MatchState, command_name: str, parent: MatcherFactory):
                self.initial_state = initial_state
                self.previous_state_buffer = initial_state
                self.parent = parent
                self.name_buffer = None
                self.command_name = command_name

            def _new_state(self):
                return self.parent._create_empty_state()

            def _use_buffered_name(self):
                if self.name_buffer is not None:
                    result = self.name_buffer
                    self.name_buffer = None
                else:
                    result = None
                return result

            def visit_root(self, root: RootComponent):
                root.get_content().accept_visitor(self)
                prev = self.previous_state_buffer
                final_state = self.parent._create_empty_state(final=True)
                label = 'recognize ' + self.command_name
                self.parent._move_automatically(prev, final_state, label, None)
                self.previous_state_buffer = final_state

            def visit_sequence(self, sequence: SequenceComponent):
                content = sequence.get_content()
                for elem in content:
                    elem.accept_visitor(self)

            def visit_word(self, word: WordComponent):
                connection_name = self._use_buffered_name()
                prev = self.previous_state_buffer
                moved_to = self.parent._move_and_add_word(prev, word, connection_name)
                self.previous_state_buffer = moved_to

            def visit_matching(self, matching: MatchingComponent):
                connection_name = self._use_buffered_name()
                prev = self.previous_state_buffer
                moved_to = self.parent._move_and_add_matching(prev, matching, connection_name)
                self.previous_state_buffer = moved_to

            def visit_optional(self, optional: OptionalComponent):
                name = self._use_buffered_name()
                prev = self.previous_state_buffer

                ends_at = self.parent._move_automatically(prev, None, 'skip optional', name)
                begins_at = self.parent._move_automatically(prev, None, 'begin optional', name)

                self.previous_state_buffer = begins_at

                content = optional.get_content()
                content.accept_visitor(self)
                after_optional = self.previous_state_buffer
                self.parent._move_automatically(after_optional, ends_at, 'end optional', name)

                self.previous_state_buffer = ends_at

            def visit_list(self, lst: ListComponent):
                name = self._use_buffered_name()
                prev = self.previous_state_buffer
                begins_at = self.parent._move_automatically(prev, None, 'begin list', name)
                self.previous_state_buffer = begins_at

                content = lst.get_content()
                content.accept_visitor(self)
                after_list = self.previous_state_buffer
                ends_at = self._new_state()

                self.parent._move_automatically(after_list, begins_at, 'repeat list', name)
                self.parent._move_automatically(after_list, ends_at, 'end list', name)

            def visit_choice(self, choice: ChoiceComponent):
                name = self._use_buffered_name()
                prev = self.previous_state_buffer
                begins_at = self.parent._move_automatically(prev, None, 'begin choice', name)
                self.previous_state_buffer = begins_at

                content = choice.get_content()
                end_state = self._new_state()
                option_count = 0
                for component in content:
                    option_begin = self.parent._move_automatically(begins_at, None, f'option {option_count}', name)
                    self.previous_state_buffer = option_begin

                    component.accept_visitor(self)
                    component_ends = self.previous_state_buffer

                    # join all choices to the empty state at the end
                    self.parent._move_automatically(component_ends, end_state, 'end choice', name)
                    option_count += 1
                self.previous_state_buffer = end_state

            def visit_named(self, named: NamedComponent):
                self.name_buffer = named.get_name()
                named.get_content().accept_visitor(self)

        sig = SignatureVisitor(from_state, c_name, self)
        command.accept_visitor(sig)

    def create_namespace(self, matcher: Matcher, namespace: CommandNamespace):
        arguments = namespace.get_arguments()
        initial = matcher.get_initial_state()

        if not arguments:
            raise ValueError(f'Namespace {namespace.namespace_name} has no arguments!')

        state = initial
        for arg in arguments:
            state = self._move_and_add_word(state, arg, None)
        final_state = self._create_empty_state(final=True)
        self._move_automatically(state, final_state, f'recognize {namespace.namespace_name}', None)

    def create_command(self, command: Command, name: str) -> Matcher:
        initial = self._create_empty_state()
        self._append_command_signature(command, name, initial)
        return Matcher(initial)

    def empty_matcher(self):
        initial = self._create_empty_state()
        return Matcher(initial)  # does not match anything

    def add_command(self, matcher: Matcher, command: Command, name: str):
        initial = matcher.get_initial_state()
        self._append_command_signature(command, name, initial)
