class ErrorState:
    @staticmethod
    def enter():
        print "Entering Error State"
    @staticmethod
    def exit():
        print "Exiting Error State"
        return True
    @staticmethod
    def in_state():
        print "In Error State"