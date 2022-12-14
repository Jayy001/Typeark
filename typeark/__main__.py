from typeark.fonts import FontDictionary, Config
from typeark.events import EventsManager
from typeark.tools import ToolsManager

from loguru import logger

import sys, termios, fcntl, os

def run():
    cfg = Config(logger=logger).generate_config()
    
    if cfg:
        fonts = FontDictionary(logger=logger, config=cfg)
        fonts.load_json_dict()
        #fonts.generate_dict()
        #fonts.export_json_dict()
        
        events = EventsManager(logger=logger, config=cfg)
        tool = ToolsManager(logger=logger, events=events, config=cfg)
    
        tool.down()
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO # TODO: Make a better keyboard input
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        try:
            while 1:
                try:
                    c = sys.stdin.read(1)
                    if c:
                        char = ''.join(repr(c).replace("'", "").split())
                        data = fonts.letter_to_data(char)
                        
                        for coord in data['coords']:
                            tool.move(coord[0], coord[1])
                            
                except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
            
        tool.up()
    
if __name__ == '__main__':
    run()
    
# python -m typeark | ssh 10.11.99.1 -T "cat > /dev/input/event1"
