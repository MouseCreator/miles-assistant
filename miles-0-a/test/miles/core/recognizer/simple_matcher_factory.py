from src.miles.core.matcher.matcher import Matcher, MatchConnection, MatchState
from typing import Tuple, List



def create_simple_matcher(origin: List[Tuple[int, int, int, MatchConnection]]) -> Matcher:
    """
    Creates simple matcher defined by origin array.
    State IDs restrictions:
        - ID = 0 - initial state
        - 0 < ID <= 100 - inner state
        - 100 < ID - final state
    """
    final_state_threshold = 100
    states = {
        0: MatchState.initial()
    }

    for sample in origin:
        from_state = sample[0]
        to_state = sample[1]
        priority = sample[2]
        connection = sample[3]

        if from_state < 0 :
            raise ValueError(f'Invalid FROM state id: {from_state}')
        if to_state < 0 :
            raise ValueError(f'Invalid TO state id: {to_state}')

        if from_state not in states.keys():
            states[from_state] = MatchState(from_state, from_state > final_state_threshold)
        if to_state not in states.keys():
            states[to_state] = MatchState(to_state, to_state > final_state_threshold)
        states.get(from_state).add_connection(connection, priority, states.get(to_state))

    sorted_keys = sorted(states.keys())

    states_arr = []

    for key in sorted_keys:
        states_arr.append(states[key])

    return Matcher(states_arr)
