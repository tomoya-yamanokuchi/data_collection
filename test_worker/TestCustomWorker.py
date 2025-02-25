from multiprocessing_worker import BaseWorker
from typing import Any


# 使用例（適宜、環境や設定を渡す必要あり）
class TestCustomWorker(BaseWorker):
    def execute(self, task: Any) -> Any:
        return f"Processed {task}"
