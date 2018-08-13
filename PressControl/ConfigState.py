class ConfigState:

    def __init__(self):
        pass

    def enter(self):
        print "Entering Setup State"
        return self

    def exit(self):
        print "Exiting Setup State"
        return True

    def in_state(self):
        print "In Setup State"