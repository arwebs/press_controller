class SetupState:
    @staticmethod
    def enter():
        print "Entering Setup State"
    @staticmethod
    def exit():
        print "Exiting Setup State"
        return True
    @staticmethod
    def in_state():
        print "In Setup State"