from src.miles.core.matcher.matcher import Matcher, MatchState, ConnectionType
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet

from typing import Set

def preprocess_matcher(matcher: Matcher, matching_set : MatchingDefinitionSet):
    initial = matcher.get_initial_state()
    visited_states: Set[MatchState] = set()

    active_states = [initial]

    while len(active_states) > 0:
        for connection in initial.all_connections():

            if connection.connection_type == ConnectionType.MATCHING:
                # process matching
                pass

            dest = initial.get_destination(connection)
            if dest not in visited_states:
                active_states.append(dest)
