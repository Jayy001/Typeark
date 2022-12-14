import json, os, re
import numpy as np

from collections import OrderedDict
from subprocess import check_output, CalledProcessError

class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""

    def default(self, obj):
        if isinstance(
            obj,
            (
                np.int_,
                np.intc,
                np.intp,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
            ),
        ):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Config:
    def __init__(self, logger, location: str = "config/config.json") -> None:    
        """_summary_

        Args:
            location (str, optional): _description_. Defaults to "config/config.json".

        Returns:
            _type_: _description_
        """
        self.location = location
        self.logger = logger
        
    def generate_config(self):
        self.logger.debug("Generating config")
        return self.__load_config()
    
    @staticmethod
    def __validate_config():
        values = {
            'waitTime': int, 
            'kerningSize': int,
            'leadingSize': int, 
            'lineNumber': int,
            'fontSize': int,
            'cursorPosition': list,
            'joinPathData': bool, 
            'minDistance': float,
            'roundToNearest': float,
            'sampleFrequency': float,
            'pretty': bool,
            'prettyIndent': int    
        }
    
    def __load_config(self):
        if not os.path.isfile(self.location):
            self.logger.error("Config file does not exist")
        else:
            self.logger.debug("Opening config file")
            with open(self.location, encoding='UTF-8') as cfile:
                try:
                    return json.load(cfile)
                except Exception as why:
                    self.logger.error(f"Failed to read config file, {why}")


class FontDictionary:
    def __init__(self, logger, config) -> None:
        """_summary_

        Args:
            config (_type_): _description_
        """
        self.logger = logger
        self.config = config     
        self.current_dictionary = {}  
        
    def load_json_dict(self):
        self.logger.debug(f"Importing dictonary from {self.config['dictionaryLocation']}")
        
        with open(self.config['dictionaryLocation'], encoding='utf-8') as in_file:
            self.current_dictionary = json.load(in_file)
            
        self.logger.success("Imported to current_dictonary")
    
    def letter_to_data(self, letter):
        self.logger.debug(f"Getting coords for '{letter}'")
        
        try:
            return self.current_dictionary[letter]
        
        except Exception as why:
            self.logger.error(f"Could not import data: {why}")
            
            return {}
        
    def export_json_dict(self) -> None:
        self.logger.debug(f"Attempting to export dictonary to {self.config['dictionaryLocation']}")
        
        if not self.current_dictionary:
            self.logger.error("Failed: no contents in current dictonary")
            
            return
        
        with open(self.config['dictionaryLocation'], "w+") as out_file:
            out_file.write(json.dumps(self.current_dictionary, cls=NumpyEncoder))
    
    def generate_dict(self) -> None:
        """_summary_

        Args:
            output (str, optional): _description_. Defaults to 'config/alphabet.json'.
        """
        
        letter_offset = 0
        
        self.logger.debug(f"Generating JSON dictonary from {self.config['fontFile']} with config {self.config['configLocation']}")
        
        try:
            process = check_output(['svgpi', self.config['configLocation'], self.config['fontFile'], './.temp_svgpi_output.json'], text=True)
        except CalledProcessError as exc:
            return

        with open('./.temp_svgpi_output.json', encoding='utf-8') as svgpi_output:
            letters = json.load(svgpi_output)
            coordinates = list(letters.values())
            
            self.logger.debug("Processing coordinates")
            
            for coords in coordinates:
                current_letter = self.config['stringValue'][letter_offset]
                
                raw_x_values, raw_y_values = [], []
                
                for x, y in zip(coords[::2], coords[1::2]): # Every two items get linked
                    raw_x_values.append(x)
                    raw_y_values.append(y)
                
                # The current output is upside down,we need to flip it over
                
                raw_x_values = np.flip(raw_x_values, 0)
                raw_y_values = np.flip(raw_y_values, 0)
                raw_y_values = max(raw_y_values) - raw_y_values
                
                # Now we need to resize the points to have them from the origin (0,0) and resize them to our font
                
                x_transformation = min(raw_x_values)
                y_transformation = min(raw_y_values)
                
                resized_coordinates = []
                
                for value_offset in range(len(raw_x_values)):  # Doesn't matter which, as the lists are the same
                    resized_coordinates.append(
                        [
                            int(
                                (raw_x_values[value_offset] - x_transformation) * self.config['fontSize']
                            ),
                            int(
                                (raw_y_values[value_offset] - y_transformation) * self.config['fontSize']
                            ),
                        ]
                    )
                    
                # We also need to rotate it as its currently on its side and then zip up the values
                
                rotated_coordinates = np.rot90(np.array(resized_coordinates))
                packed_coordinates = list(zip(rotated_coordinates[0], rotated_coordinates[1]))
                
                # And then remove the duplicates to make it smaller...keeping it in order so coords don't jump around in large gaps
                
                final_coordinates = list(OrderedDict.fromkeys(packed_coordinates).keys())
                
                # Finally we need to assign it it's equivalent letter and add it to our output
                
                self.logger.debug(f"Appending to output: {current_letter}, max point: {max(final_coordinates)}, min_point: {min(final_coordinates)}")
                
                self.current_dictionary[current_letter] = {
                    "metadata": {"max_point": max(final_coordinates), "min_point": min(final_coordinates)},
                    "coords": final_coordinates,
                }
                
                letter_offset += 1
                
        # Cleaning up the files
    
        self.logger.debug("Removing ./.temp_svgpi_output.json")
        os.remove("./.temp_svgpi_output.json")