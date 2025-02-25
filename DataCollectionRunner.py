import time
from typing import Type, Any
from .DataCollectionManager import DataCollectionManager
from multiprocessing_worker import BaseWorker
from domain_object.builder import DomainObject

class DataCollectionRunner:
    def __init__(self,
            num_workers  : int,
            worker_class : Type[BaseWorker],
            domain_object: DomainObject,
        ):
        self.manager = DataCollectionManager(num_workers, worker_class, domain_object)

    def run(self, tasks: Any):
        self.manager.start_workers()
        for task in tasks:
            self.manager.add_task(task)
        time.sleep(2)  # 実行待機
        self.manager.stop_workers()
        return self.manager.get_results()
