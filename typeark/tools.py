from math import sqrt

class ToolsManager:
    def __init__(self, logger, events, config) -> None:
        self.logger = logger
        self.__mode = 320
        self.events = events
        self.config = config
        self.current_pos = [0, 0]

    def change_mode(self, mode):
        if mode == "rubber":
            self.__mode = 321
        elif mode == "pen":
            self.__mode = 320
        else:
            self.logger.error("Invalid mode given")

    def down(self, start_coord_x=0, start_coord_y=0):
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
        self.events.output(packed_events) #TODO: Auto sync
        self.current_pos = [start_coord_x, start_coord_y]
    
    def move(self, x_coord, y_coord):
        x_coord += self.current_pos[0]
        y_coord += self.current_pos[1]
        
        if sqrt((x_coord-self.current_pos[0])**2+(y_coord-self.current_pos[1])**2) > self.config['maxJump']:
            self.up()
            self.down(x_coord, y_coord)
        else:
            packed_move_events = self.events.pack_events([
                [3, 0, x_coord],
                [3, 1, y_coord],
                self.events.sync()
            ])
            self.events.output(packed_move_events)
            self.current_pos = [x_coord, y_coord]
            
    def up(self):
        packed_events = self.events.pack_events([
            [1, 330, 0],
            [3, 25, 80],
            [1, self.__mode, 0],
            self.events.sync()
        ])
        self.events.output(packed_events)