from typeark.font_manager import FontDictionary, Config
from typeark.remote_manager import FileRemote

def run():
    cfg = Config().generate_config()
    
    if cfg:
        fd = FontDictionary(cfg)
        fd.save_json_dict()

if __name__ == '__main__':
    run()
    