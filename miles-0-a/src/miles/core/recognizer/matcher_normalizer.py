from src.miles.core.matcher.matcher import Matcher


class NormalizedMatcher:
    """
    For priority control, it will be essential to use Normalized Matchers.
    Normalized matchers will have complex connections, that contain multiple actions
    This approach provides several important advantages:
        - easier to calculate priorities. Taking max() or first non-zero priority from the group is easier,
        when connections are normalized;
        - No redundant connections that result in an infinite loop.
        For example, [{a}] - list of optionals may have an infinite loop
        - Automatic connections are still possible because of final states.
        For example, (state) --auto--> (final) cannot be rewritten as word or matching connection
    Challenges:
        - Normalization algorithm
        - Adjust text recognized to handle complex connections properly
    """
    pass

def normalize(matcher: Matcher):
    pass