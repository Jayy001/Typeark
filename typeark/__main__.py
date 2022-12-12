from typeark.fonts import FontDictionary, Config
from typeark.remote import FileRemote
from typeark.events import EventsInjector
from typeark.tools import ToolsManager

from loguru import logger

def run():
    cfg = Config(logger=logger).generate_config()
    
    if cfg:
        fd = FontDictionary(logger=logger, config=cfg)
        #fd.generate_dict()
        #fd.export_json_dict()
        
        fr = FileRemote(logger=logger, config=cfg)
        ei = EventsInjector(logger=logger, remote=fr, config=cfg)
        tm = ToolsManager(logger=logger, events=ei, config=cfg)
    
        tm.activate(5000, 5000)
        fr.close_session()
    
if __name__ == '__main__':
    run()
    