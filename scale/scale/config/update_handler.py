from config.config_interface import ConfigInterface
from watchdog.events import DirDeletedEvent, DirModifiedEvent, FileDeletedEvent, FileModifiedEvent, FileSystemEventHandler
from typing import Union


class ConfigUpdateHandler(FileSystemEventHandler):
    def __init__(self, config: ConfigInterface, config_path: str):
        self._config = config
        self._config_path = config_path

    def on_modified(self, event: Union[DirModifiedEvent, FileModifiedEvent]) -> None:
        if event.is_directory:
            return  
        print(f"Configuration in {event.src_path} has been updated. Reloading...")
        self._config.update_config()

    def on_created(self, event):
        if event.is_directory:
            return
        print(f"New configuration file {event.src_path} has been created. Loading configuration...")
        self._config.update_config()

    def on_deleted(self, event: Union[DirDeletedEvent, FileDeletedEvent]) -> None:
        if event.is_directory:
            return
        print(f"Configuration file {event.src_path} has been deleted. Removing configuration...")
        self._config.update_config()
