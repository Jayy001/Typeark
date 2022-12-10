import paramiko
from io import BytesIO

class FileRemote:
    def __init__(self, config) -> None: #TODO: More specific exceptions
        self.session = paramiko.SSHClient
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def open_session(self) -> None: #TODO: Should return None, ask help on typehints
        try:
            self.session.connect('10.11.99.1', username='root', password=self.config['rmPassword'])
            self.file_manager = self.session.opensftp()
        except Exception as error:
            return error
    
    def inject_contents(self, contents, remote_file: str) -> None: #TODO: Inject or write?
        if type(contents) == "str":
            contents = contents.encode()
        try:
            self.file_manager.putfo(BytesIO(contents), remote_file)
        except Exception as error:
            return error
    
    def close_session(self):
        self.file_manager.ftp.close()
        self.session.close()