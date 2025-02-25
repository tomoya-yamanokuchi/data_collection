import time
from typing import Type, Any
from .DataCollectionManager import DataCollectionManager
from multiprocessing_worker import BaseWorker

class DataCollectionRunner:
    def __init__(self,
            num_workers : int,
            worker_class: Type[BaseWorker],
            *worker_args: Any
        ):
        self.manager = DataCollectionManager(num_workers, worker_class, *worker_args)

    def run(self, tasks):
        self.manager.start_workers()
        for task in tasks:
            self.manager.add_task(task)
        time.sleep(2)  # 実行待機
        self.manager.stop_workers()
        return self.manager.get_results()
