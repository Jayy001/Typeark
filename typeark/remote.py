import paramiko, sys
from io import BytesIO

class FileRemote:
    def __init__(self, logger, config) -> None: #TODO: More specific exceptions
        self.logger = logger
        self.config = config
        
        logger.debug("Starting paramiko session")
        
        self.session = paramiko.client.SSHClient()
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if self.open_session():
            self.logger.success("Started session to the ReMarkable")
        else:
            sys.exit(1)
        
        self.active_file = self.file_manager.file(self.__get_input_file(), "ab", -1)
        
    def __get_input_file(self):
        self.logger.debug("Getting pen input file")
        
        stdin, stdout, stderr = self.session.exec_command("cat /sys/devices/soc0/machine")
        
        if "reMarkable 2.0" in str(stdout.read()):
            self.logger.success("Set file to /dev/input/event1")
            return "/dev/input/event1"
        else:
            self.logger.success("Set file to {}")
            return "" #TODO: Find pen file for this!
    
    def open_session(self) -> bool: 
        try:
            self.session.connect('10.11.99.1', username='root', password=self.config['rmPassword'])
            self.file_manager = self.session.open_sftp()
            
            return True
        
        except Exception as why:
            self.logger.error(f"Could not connect to the ReMarkable: {why}")
    
    def write_file_contents(self, contents) -> None: 
        try:
            self.active_file.write(contents)
        except Exception as why:
            self.logger.error(f"Could not write {contents} to file: {why}")
            return why
    
    def close_session(self):
        self.active_file.flush()
        
        self.file_manager.close()
        self.session.close()
        
        self.logger.success("Closed remote session")