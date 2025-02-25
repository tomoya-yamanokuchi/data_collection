import time
from domain_object.builder import DomainObject
from ..worker import CustomWorker
from ..DataCollectionRunner import DataCollectionRunner



class MockupDataCollection:
    def __init__(self, domain_object: DomainObject):
        self.domain_object = domain_object

    def time_start(self):
        self.__time_start = time.time()

    def time_stop(self):
        self.__time_stop = time.time()
        elapsed_time = self.__time_stop - self.__time_start
        print(" MockupDataCollection: elapsed_time = {} [sec]".format(elapsed_time))

    def run(self):
        runner = DataCollectionRunner(num_workers=2, worker_class=CustomWorker, domain_object='ExampleDomain')
        tasks = [f"Task {i}" for i in range(5)]
        results = runner.run(tasks)
        print(results)
