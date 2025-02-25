import multiprocessing as mp
from multiprocessing_worker import BaseWorker
from typing import Any


# 使用例（適宜、環境や設定を渡す必要あり）
class TestCustomWorker2(BaseWorker):
    def __init__(self, input_queue: mp.Queue, output_queue: mp.Queue):
        self.input_queue  = input_queue
        self.output_queue = output_queue

    def execute(self, task: Any) -> Any:
        self.input_queue.put(task)
        self.output_queue.put(f"Processed {task}")  # ここでデータを送る
        return self.output_queue.get()
