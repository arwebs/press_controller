class StartupState:
    @staticmethod
    def enter():
        print "Entering Startup State"
    @staticmethod
    def exit():
        print "Exiting Startup State"
        return True
    @staticmethod
    def in_state():
        print "in Startup State"