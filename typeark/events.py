import struct, time

class EventsInjector:
    def __init__(self, logger, remote, config) -> None:
        self.logger = logger
        self.config = config
        self.remote = remote
        
    def __pack_values(self, typ, code, value):
        return struct.pack("QHHi", int(time.time()), typ, code, value)

    def __sync(self):
        self.logger.debug("Sending sync")
        return self.__pack_values(0, 0, 0)
    
    def inject(self, events):
        self.logger.debug("Injecting events")
        
        for event in events:
            time.sleep(self.config['waitTime'])
                
            self.remote.write_file_contents(event)
    
    def pack_commands(self, commands):
        results = []
        
        for command in commands:
            if type(command) == bytes:
                self.logger.debug("Command is already in byte form, skipping")
                continue
            
            if len(command) != 3:
                self.logger.error("Invalid command given")
                continue
                
            try:    
                results.append(self.__pack_values(command[0], command[1], command[2]))
                
            except Exception as why:
                self.logger.error(f"Could not pack {command} due to: {why}")
                continue

        # results.append(self.__sync())
        return results
        