from typing import Any
import multiprocessing as mp
from multiprocessing_worker import BaseWorker


class CustomWorker(BaseWorker):
    def __init__(self, output_queue: mp.Queue, domain_object: Any):  #
        self.output_queue  = output_queue
        self.domain_object = domain_object

    def execute(self, task: Any) -> Any:
        if task is None:
            return None
        result = f"Processed {task}"
        self.output_queue.put(result)  # 結果を送信
        return result
