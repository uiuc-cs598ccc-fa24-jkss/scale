import os
import asyncio
import threading
from trace_consumer import TraceConsumer
from trace_processor import TraceProcessor
from config.config_manager import ConfigManager
from config.update_handler import ConfigUpdateHandler
from orchestration.kubernetes import KubernetesClient
from watchdog.observers.inotify import InotifyObserver
import logging


async def main():
    print("Starting Trace Modeler...")
    client_url = os.getenv("TRACE_BACKEND_URL", "http://tempo:3200")
    config_path = os.getenv("CONFIG_SPEC_PATH", "/app/config/specs")
    target_namespace = os.getenv("TARGET_NAMESPACE", "default")

    orchestrator = KubernetesClient(namespace=target_namespace, in_cluster=True)
    config = ConfigManager(config_path)
    update_handler = ConfigUpdateHandler(config=config, config_path=config_path)

    observer = InotifyObserver()
    observer.schedule(update_handler, config_path, recursive=True)    

    # run the observer in a separate thread
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()
    
    try: 
        processor = TraceProcessor(client_url=client_url, config=config, orchestrator=orchestrator)
        async with TraceConsumer(processor) as consumer:
            await consumer.consume()
    finally:
        observer.stop()
        observer.join()
        processor.stop_metrics_reporting()        


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s')
    asyncio.run(main())
