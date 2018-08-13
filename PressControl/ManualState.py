class ManualState:
    def __init__(self):
        pass
    def enter(self):
        print "Entering Manual State"
        return self
    def exit(self):
        print "Exiting Manual State"
        return True
    def in_state(self):
        print "In Manual State"