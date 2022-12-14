import struct, time, sys

class EventsManager:
    def __init__(self, logger, config) -> None:
        self.logger = logger
        self.config = config
        
    def __pack_values(self, typ, code, value):
        return struct.pack("QHHi", int(time.time()), typ, code, value)

    def sync(self):
        return self.__pack_values(0, 0, 0)
    
    def output(self, events):
        self.logger.debug("Outputting events")
        
        for event in events:
            sys.stdout.buffer.write(event)
    
    def pack_events(self, events):
        results = []
        
        for command in events:
            if type(command) == bytes:
                results.append(command)
                continue
            
            elif len(command) != 3:
                self.logger.error("Invalid command given")
                continue
                
            try:  
                results.append(self.__pack_values(command[0], command[1], command[2])) #TODO: Setup auto-syncing
                
            except Exception as why:
                self.logger.error(f"Could not pack {command} due to: {why}")
                continue

        return results
        