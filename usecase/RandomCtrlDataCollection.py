import os
import time
from domain_object.builder import DomainObject
from ..worker import RandomCtrlDataCollection_with_fixed_init_ctrl
from ..DataCollectionRunner import DataCollectionRunner
from domain_object.builder import DomainObject


class RandomCtrlDataCollection:
    def __init__(self):
        pass

    def time_start(self):
        self.__time_start = time.time()

    def time_stop(self):
        self.__time_stop = time.time()
        elapsed_time = self.__time_stop - self.__time_start
        print(" iCEMDataCollection elapsed_time = {} [sec]".format(elapsed_time))


    def run(self, domain_object: DomainObject):
        worker = RandomCtrlDataCollection_with_fixed_init_ctrl
        runner = DataCollectionRunner(num_workers=2, worker_class=worker, domain_object=domain_object)
        tasks = [f"Task {i}" for i in range(5)]
        results = runner.run(tasks)
        print(results)
