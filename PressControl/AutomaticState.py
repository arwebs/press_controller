class AutomaticState:
    def __init__(self):
        pass

    def enter(self):
        print "Entering Automatic State"
        return self
    def exit(self):
        print "Exiting Automatic State"
        return True
    def in_state(self):
        print "In Automatic State"