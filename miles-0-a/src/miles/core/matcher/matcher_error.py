class MatcherError(ValueError):
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)

    @staticmethod
    def __new__(*args, **kwargs):
        super.__new__(*args, **kwargs)
