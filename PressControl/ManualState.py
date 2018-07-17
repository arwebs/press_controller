class ManualState:
    @staticmethod
    def enter():
        print "Entering Manual State"
    @staticmethod
    def exit():
        print "Exiting Manual State"
        return True
    @staticmethod
    def in_state():
        print "In Manual State"