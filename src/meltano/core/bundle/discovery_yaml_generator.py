import os
import re
from typing import Dict, Any
from ruamel.yaml import YAML
import pathlib

yaml = YAML()

DISCOVERY_VERSION = 19
MELTANO_DIR = "discovery_definitions/"
DISCOVERY_FILE = "discovery_new.yml"

def generate_discovery_yaml():
    discovery_dict: Dict[str, Any] = {}
    discovery_dict["version"] = DISCOVERY_VERSION

    for root, subdir, files in os.walk(MELTANO_DIR):
        meltano_type = re.sub(MELTANO_DIR, "", root)
        if meltano_type == "":
            continue
        meltano_array = []

        for file in files:
            with open(os.path.join(root, file), "r") as plugin_file:
                plugin_data = yaml.load(plugin_file)

            meltano_array.append(plugin_data)

        discovery_dict[meltano_type] = meltano_array

    with open(str(pathlib.Path(__file__).parent.resolve()) + "/" + DISCOVERY_FILE, "w") as outfile:
        yaml.dump(discovery_dict, outfile)
