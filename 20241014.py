#/refactoring dashboard for centralized classes of plotly figures

class figs_all:
    def __init__(self):
        self.physical = self.figs_physical()

    class figs_physical:
        def __init__(self):
            self.run = None
            self.weight = None