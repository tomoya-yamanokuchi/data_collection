import copy
import time
import random
import numpy as np
import multiprocessing as mp
from typing import Any
# from .DataCollectionPlanningDomainObjectDict import DataCollectionPlanningDomainObjectDict
from icem_torch.icem_subparticle.forward_model_multiprocessing import PlanningQueueParamDict
# from robel_dclaw_env.domain.environment.instance.simulation.base_environment import AbstractEnvironment
from service import NTD, wait_time, create_rectangular_init_fixed_ctrl
# from ..AbstractPlanning import AbstractPlanning
from multiprocessing_worker import BaseWorker
from domain_object.builder import DomainObject
from robot_env.instance import RobelDclawEnv
from icem.adaptive_sampling import AdaptiveSamplingDistribution
from icem.adaptive_sampling.mean.initialization import UniformInitialization
from icem.adaptive_sampling.std.initialization import FixedStdInitialization


class RandomCtrlDataCollection_with_fixed_init_ctrl(BaseWorker):
    def __init__(self,
             output_queue : mp.Queue,
             domain_object: DomainObject
        ):
        self.output_queue = output_queue
        # ----
        self.domain_object              = domain_object
        self.env_object                 = domain_object.env_obj
        self.config_env                 = domain_object.config_env
        self.sampling_dist              = domain_object.adaptive_sampling_dist_uniform
        self.colored_population_sampler = domain_object.colored_population_sampler
        self.trajectory_evaluator       = domain_object.trajectory_evaluator
        self.env_data_container         = domain_object.env_data_container
        self.env_data_repository        = domain_object.env_data_repository
        self.config_icem                = domain_object.config_icem_sub
        # self.xml_path                = domain_object_dict['xml_path']
        # self.TaskSpaceAbsValueObject = domain_object_dict['TaskSpaceAbsValueObject']
        # self.control_adaptor         = domain_object_dict['control_adaptor']
        self.beta_list = self.config_icem.icem.colored_noise_exponent

        # ---
    def execute(self, task_index: int, task_data: np.ndarray, total_tasks: int) -> Any:
        wait_time(const=5, seed=1)
        # ---
        env: RobelDclawEnv = self.env_object(self.domain_object)
        # ---
        self.sampling_dist.reset_distribution(prev_mean=None)
        # ---
        saved_flag = False
        while saved_flag is False:
            u_sample = self.colored_population_sampler.sample(
                sampling_dist = self.sampling_dist,
                num_sample    = 1,
                beta          = random.choice(self.beta_list),
            )
            num_batch, step, dim_ctrl = u_sample.shape; # print("u_sample.shape = ", u_sample.shape)

            # --- replace init with fixed ctrl ---
            step_fixed               = self.config_icem.icem.step_fixed; print("step_fixed = ", step_fixed)
            task_space_diff_ctrl     = create_rectangular_init_fixed_ctrl(step_fixed=step_fixed)
            u_sample[:, :step_fixed] = task_space_diff_ctrl

            # ---- create cumurative abs ctrl ---
            task_space_position_init = init_state["task_space_position"] # ValueObject (batch, step, dim_u) == (1, 1, 6)
            self.control_adaptor.set_task_space_position_init(task_space_position_init)
            task_space_abs_ctrl = (task_space_position_init.value[:, :, :dim_ctrl] + u_sample.cumsum(axis=1))

            # task_space_abs_ctrl      = self.TaskSpaceAbsValueObject(task_space_abs_ctrl).value
            print(f"task_space_position_init.value.shape = {task_space_position_init.value.shape}")
            print(f"task_space_abs_ctrl.shape = {task_space_abs_ctrl.shape}")
            # print(f"task_space_abs_ctrl_init = {task_space_abs_ctrl_init}")
            # print(f"task_space_abs_ctrl[:, 0, :] = {task_space_abs_ctrl[:, 0, :]}")
            # print(f"u_sample.cumsum(axis=1) = {u_sample.cumsum(axis=1)[:, 0]}")
            # print(f"u_sample.min(), u_sample.max() = {u_sample.min(), u_sample.max()}")

            # import ipdb; ipdb.set_trace()
            # ----
            # print("u_sample = {}".format(u_sample[0, :step_fixed+2, :2]))
            # import sys
            # sys.exit()
            # -----------------------------------------------------
            assert num_batch == 1
            # ---
            self.env_data_container.reset()
            # ---
            env.set_xml_path(self.xml_path)
            env.reset(init_state)# ; print("2. env.reset(init_state)")
            # --- stabilaing init position -----
            env.set_task_space_ctrl(task_space_position_init)
            env.step(is_view=False)
            # ----
            for t in range(step):
                image = env.render()
                state = env.get_state() #; print("4. state = env.get_state()") if n==0 and t==0 else None
                # if t == 1: next_state = copy.deepcopy(state)
                task_space_ctrl = self.control_adaptor.modelCtrl2envCtrl(task_space_abs_ctrl[0, t])
                # -----
                # print("----------------------------------------------------------")
                # print("(t={}) task_space_position  = {}".format(t, state["task_space_position"].value.squeeze()[:5]))
                # print("(t={}) task_space_ctrl      = {}".format(t, task_space_ctrl.value.squeeze()[:5]))
                # print("----------------------------------------------------------")
                # if t == 1:
                    # import sys; sys.exit()
                # -----
                ctrl                 = env.set_task_space_ctrl(task_space_ctrl)
                # if t == 0: ctrl_t = copy.deepcopy(ctrl)
                env.step()
                # ----
                self.env_data_container.append_image(image)
                self.env_data_container.append_state(state)
                self.env_data_container.append_ctrl(ctrl)
            # ------
            if self.trajectory_evaluator.evaluate(self.env_data_container.get_state_list()):
                # 条件を満たす場合のみ保存処理
                self.env_data_repository.open(filename='indexChunk{}_sequence{}'.format(index_chunk, saved_count))
                self.env_data_repository.assign(self.env_data_container.get_image_list(), name="image")
                self.env_data_repository.assign(self.env_data_container.get_state_list(), name="state")
                self.env_data_repository.assign(self.env_data_container.get_ctrl_list(), name="ctrl")
                self.env_data_repository.close()
                # ---
                saved_count += 1
                time.sleep(1)
                print("<< success : {} >>".format(saved_count))
            else:
                # print("<< fault >>")
                pass
            iter_loop += 1
        # -------
        result_dict = {"index_chunk": index_chunk}
        self.queue_output.put(result_dict)
        self.queue_input.task_done()




        self.output_queue.put(result)  # 結果を送信
