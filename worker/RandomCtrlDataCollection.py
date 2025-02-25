import os
import time
from domain_object.builder import DomainObject
from service import file_copy_and_rename


class RandomCtrlDataCollection:
    def __init__(self, domain_object: DomainObject):
        self.config_icem              = domain_object.config_icem_sub
        self.xml_str                  = domain_object.xml_str
        self.xml_generator            = domain_object.xml_generator
        self.file_copy_manager        = domain_object.file_copy_manager
        self.icem_subparticle_manager = domain_object.icem_subparticle_manager
        self.state_t                  = domain_object.init_state

    def time_start(self):
        self.__time_start = time.time()

    def time_stop(self):
        self.__time_stop = time.time()
        elapsed_time = self.__time_stop - self.__time_start
        print(" iCEMDataCollection elapsed_time = {} [sec]".format(elapsed_time))

    def generate_xml_model(self):
        self.xml_generator.generate(fname="object_current")

    def copy_xml(self):
        self.file_copy_manager.copy_xml()
        self.file_copy_manager.copy_origin_png()
        self.file_copy_manager.copy_aligned_png()

    def set_model_file(self):
        self

    def run_multiprocessing_data_collection(self, current_step):
        self.icem_subparticle_manager.optimize(current_step, init_state=self.state_t, u_nominal=None)

