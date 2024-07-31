import configparser
import sys
import os 

def create_config(save_path: str, locations_path:str, existing_flags_paths:str)-> bool: 
    filename = "custom_mutator.ini" 

    if not os.path.exists(locations_path) and not os.path.exists(existing_flags_paths) and not os.path.exists(save_path): 
        print("[!] One of the given paths does not exist.")
        return False 

    config = configparser.ConfigParser()
    if os.path.exists(os.path.join(save_path, filename)): 
        config.read(os.path.join(save_path, filename))
        config['weighted_input_mutator']['locations_path'] = locations_path
        config['weighted_input_mutator']['existing_flags_path'] = existing_flags_paths
    else:
        config['weighted_input_mutator'] = {'locations_path': locations_path,
                                            'existing_flags_path': existing_flags_paths,
                                            'consider_stdin': "off", 
                                            'valid_characters': "a"}

    with open(os.path.join(save_path,filename), 'w') as configfile: 
        config.write(configfile)

if __name__ == "__main__": 
    pass