class Relay:
    @staticmethod
    def init(logger=None, bus_nr=1):
        print("[MOCK RELAY] Initialized")

    @staticmethod
    def on_1():
        print("[MOCK RELAY] Relay 1 ON")

    @staticmethod
    def off_1():
        print("[MOCK RELAY] Relay 1 OFF")

    @staticmethod
    def on_3():
        print("[MOCK RELAY] Relay 3 ON")

    @staticmethod
    def off_3():
        print("[MOCK RELAY] Relay 3 OFF")
