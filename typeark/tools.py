

class ToolsManager:
    def __init__(self, logger, events, config) -> None:
        self.logger = logger
        self.__mode = 320
        self.events = events

    def change_mode(self, mode):
        if mode == "rubber":
            self.__mode = 321
        elif mode == "pen":
            self.__mode = 320
        else:
            print("Invalid mode given")

    def activate(self, start_coord_x, start_coord_y):
        packed_events = self.events.pack_events([
            [1, self.__mode, 1],
            [1, 330, 0],
            [3, 24, 0],
            [3, 25, 80],
            self.events.sync(),
            [3, 0, start_coord_x],
            [3, 1, start_coord_y],
            [3, 25, 0],
            [3, 26, 0],
            [3, 27, 0],
            self.events.sync(),
            [1, 330, 1],
            self.events.sync()
        ])
        self.events.inject(packed_events)
        
    def stop(self):
        packed_events = self.events.pack_events([
            [1, 330, 0],
            [3, 25, 80],
            [1, self.__mode, 0],
            self.events.sync()
        ])
        self.events.inject(packed_events)