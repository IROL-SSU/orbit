# Copyright (c) 2022-2024, The ORBIT Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import gymnasium as gym
import os

from . import agents
from . import ik_abs_env_cfg, ik_rel_env_cfg, joint_pos_env_cfg, ik_rel_env_cfg_sac


##
# Register Gym environments.
##

##
# Joint Position Control
##

gym.register(
    id="Isaac-Grasp-Object-Franka-v0",
    entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": joint_pos_env_cfg.FrankaGraspObjectEnvCfg,
        "rsl_rl_cfg_entry_point": agents.rsl_rl_cfg.GraspPPORunnerCfg,
        "skrl_cfg_entry_point": f"{agents.__name__}:skrl_ppo_cfg.yaml",
    },
    disable_env_checker=True,
)

gym.register(
    id="Isaac-Grasp-Object-Franka-Play-v0",
    entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": joint_pos_env_cfg.FrankaGraspObjectEnvCfg_PLAY,
        "rsl_rl_cfg_entry_point": agents.rsl_rl_cfg.GraspPPORunnerCfg,
        "skrl_cfg_entry_point": f"{agents.__name__}:skrl_ppo_cfg.yaml",
    },
    disable_env_checker=True,
)

# ##
# # Inverse Kinematics - Absolute Pose Control
# ##

gym.register(
    id="Isaac-Grasp-Object-Franka-IK-Abs-v0",
    entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": ik_abs_env_cfg.FrankaGraspObjectEnvCfg,
        "rsl_rl_cfg_entry_point": agents.rsl_rl_cfg.GraspPPORunnerCfg,
        "skrl_cfg_entry_point": f"{agents.__name__}:skrl_ppo_cfg.yaml",
    },
    disable_env_checker=True,
)

gym.register(
    id="Isaac-Grasp-Object-Franka-IK-Abs-Play-v0",
    entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": ik_abs_env_cfg.FrankaGraspObjectEnvCfg_PLAY,
        "rsl_rl_cfg_entry_point": agents.rsl_rl_cfg.GraspPPORunnerCfg,
        "skrl_cfg_entry_point": f"{agents.__name__}:skrl_ppo_cfg.yaml",
    },
    disable_env_checker=True,
)

# ##
# # Inverse Kinematics - Relative Pose Control
# ##

# gym.register(
#     id="Isaac-Lift-Cube-Franka-IK-Rel-v0",
#     entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
#     kwargs={
#         "env_cfg_entry_point": ik_rel_env_cfg.FrankaGraspObjectEnvCfg,
#         "rsl_rl_cfg_entry_point": agents.rsl_rl_cfg.LiftCubePPORunnerCfg,
#         "skrl_cfg_entry_point": f"{agents.__name__}:skrl_ppo_cfg.yaml",
#         "robomimic_bc_cfg_entry_point": os.path.join(agents.__path__[0], "robomimic/bc.json"),
#     },
#     disable_env_checker=True,
# )

# gym.register(
#     id="Isaac-Lift-Cube-Franka-IK-Rel-Play-v0",
#     entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
#     kwargs={
#         "env_cfg_entry_point": ik_rel_env_cfg.FrankaGraspObjectEnvCfg_PLAY,
#         "rsl_rl_cfg_entry_point": agents.rsl_rl_cfg.LiftCubePPORunnerCfg,
#         "skrl_cfg_entry_point": f"{agents.__name__}:skrl_ppo_cfg.yaml",
#     },
#     disable_env_checker=True,
# )

# gym.register(
#     id="Isaac-Lift-Cube-Franka-IK-Rel-SAC-v0",
#     entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
#     kwargs={
#         "env_cfg_entry_point": ik_rel_env_cfg_sac.FrankaGraspObjectEnvCfg,
#         "skrl_cfg_entry_point": f"{agents.__name__}:skrl_sac_cfg.yaml",
#     },
#     disable_env_checker=True,
# )
