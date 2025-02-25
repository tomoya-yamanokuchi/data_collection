import multiprocessing as mp
from typing import Any, Type
from multiprocessing_worker import WorkerProcess, BaseWorker
from domain_object.builder import DomainObject

class DataCollectionManager:
    def __init__(self,
            num_workers  : int,
            worker_class : Type[BaseWorker],
            domain_object: DomainObject
        ):
        if not issubclass(worker_class, BaseWorker):
            raise TypeError(f"worker_class must be a subclass of BaseWorker, but got {worker_class}")

        self.input_queue  = mp.Queue()
        self.output_queue = mp.Queue()
        self.processes    = []

        for _ in range(num_workers):
            p = WorkerProcess(self.input_queue, self.output_queue, worker_class, domain_object)
            self.processes.append(p)

    def start_workers(self):
        for _p in self.processes:
            p: mp.Process = _p
            p.start()

    def add_task(self, task: Any):
        self.input_queue.put(task)

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
