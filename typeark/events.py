import struct, time

class EventsInjector:
    def __init__(self, logger, remote, config) -> None:
        self.logger = logger
        self.config = config
        self.remote = remote
        
    def __pack_values(self, typ, code, value):
        return struct.pack("QHHi", int(time.time()), typ, code, value)

    def sync(self):
        return self.__pack_values(0, 0, 0)
    
    def inject(self, events):
        self.logger.debug("Injecting events")
        self.remote.write_file_contents(events)
    
    def pack_events(self, events):
        results = []
        
        for command in events:
            if type(command) == bytes:
                self.logger.debug("Sync command added")
                results.append(command)
            
            elif len(command) != 3:
                self.logger.error("Invalid command given")
                continue
                
            try:  
                results.append(self.__pack_values(command[0], command[1], command[2])) #TODO: Setup auto-syncing
                
            except Exception as why:
                self.logger.error(f"Could not pack {command} due to: {why}")
                continue

        return results
        