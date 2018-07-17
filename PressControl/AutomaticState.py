class AutomaticState:
    @staticmethod
    def enter():
        print "Entering Automatic State"
    @staticmethod
    def exit():
        print "Exiting Automatic State"
        return True
    @staticmethod
    def in_state():
        print "In Automatic State"