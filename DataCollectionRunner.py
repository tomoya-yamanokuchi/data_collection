import time
from typing import Type, Any
from .DataCollectionManager import DataCollectionManager
from multiprocessing_worker import BaseWorker
from domain_object.builder import DomainObject


class DataCollectionRunner:
    def __init__(self, num_workers: int, worker_class: Type[BaseWorker], domain_object: DomainObject):
        self.manager       = None
        self.num_workers   = num_workers
        self.worker_class  = worker_class
        self.domain_object = domain_object

    def run(self, input_data):
        total_tasks = len(input_data)
        self.manager = DataCollectionManager(self.num_workers, self.worker_class, self.domain_object, total_tasks)

        self.manager.start_workers()
        for index, data in enumerate(input_data):
            self.manager.add_task(index, data)  # タスクのインデックスを渡す

        time.sleep(2)  # 実行待機
        self.manager.stop_workers()
        return self.manager.get_results()
