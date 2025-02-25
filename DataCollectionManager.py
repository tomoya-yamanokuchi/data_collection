import multiprocessing as mp
from typing import Any, Type
from multiprocessing_worker import WorkerProcess, BaseWorker
from domain_object.builder import DomainObject

class DataCollectionManager:
    def __init__(self, num_workers: int, worker_class: Type[BaseWorker], domain_object: DomainObject, total_tasks: int):
        if not issubclass(worker_class, BaseWorker):
            raise TypeError(f"worker_class must be a subclass of BaseWorker, but got {worker_class}")

        self.input_queue  = mp.Queue()
        self.output_queue = mp.Queue()
        self.processes    = []
        self.total_tasks  = total_tasks
        self.task_counter = mp.Value('i', 0)  # 共有カウンター（整数型）

        for _ in range(num_workers):
            p = WorkerProcess(self.input_queue, self.output_queue, worker_class, domain_object, self.task_counter, total_tasks)
            self.processes.append(p)

    def start_workers(self):
        for _p in self.processes:
            p: mp.Process = _p
            p.start()

    def add_task(self, index: int, task_data: Any):
        self.input_queue.put((index, task_data))  # タスクを (index, data) の形式で送信

    def stop_workers(self):
        for _ in self.processes:
            self.input_queue.put(None)  # 終了信号
        for _p in self.processes:
            p: mp.Process = _p
            p.join()

    def get_results(self):
        results = []
        while not self.output_queue.empty():
            results.append(self.output_queue.get())
        return results
