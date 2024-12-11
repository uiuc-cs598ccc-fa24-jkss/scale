
import os
from dotenv import dotenv_values

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

config = dotenv_values(f"{SCRIPT_DIR}/../.env")


def show_config():
    print (f"config: {config}")

    print(os.path.exists(".."))
    print(os.path.exists(config["K8S_HOME"]))