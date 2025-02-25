import multiprocessing as mp
from typing import Any, Type
from multiprocessing_worker import WorkerProcess, BaseWorker


class DataCollectionManager:
    def __init__(self,
            num_workers: int,
            worker_class: Type[BaseWorker],
            *worker_args: Any
        ):
        if not issubclass(worker_class, BaseWorker):
            raise TypeError(f"worker_class must be a subclass of BaseWorker, but got {worker_class}")

        self.task_queue   = mp.Queue()
        self.result_queue = mp.Queue()
        self.processes    = []

        for _ in range(num_workers):
            p = WorkerProcess(self.task_queue, self.result_queue, worker_class, *worker_args)
            self.processes.append(p)

    def start_workers(self):
        for proc in self.processes:
            p : mp.Process = proc
            p.start()

    def add_task(self, *task_args: Any):
        self.task_queue.put(task_args)

    def stop_workers(self):
        for _ in self.processes:
            self.task_queue.put(None)  # 終了信号
        for proc in self.processes:
            p : mp.Process = proc
            p.join()

    def get_results(self):
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        return results
