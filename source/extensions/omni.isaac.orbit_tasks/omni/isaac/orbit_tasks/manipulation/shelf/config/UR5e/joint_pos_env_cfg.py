import math
from omni.isaac.orbit.utils import configclass

import omni.isaac.orbit_tasks.manipulation.shelf.mdp as mdp
from omni.isaac.orbit_tasks.manipulation.shelf.shelf_grasp_env_cfg_v2 import ShelfEnvCfg

"""
Pre-defined configs
"""

from omni.isaac.orbit_assets import UR5e_CFG, UR5e_2f85_CFG
from omni.isaac.orbit.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from omni.isaac.orbit.sim.schemas.schemas_cfg import RigidBodyPropertiesCfg
from omni.isaac.orbit.sim.spawners.from_files.from_files_cfg import UsdFileCfg
from omni.isaac.orbit.markers.config import FRAME_MARKER_CFG  # isort: skip
from omni.isaac.orbit_assets.franka import FRANKA_PANDA_CFG  # isort: skip
from omni.isaac.orbit.sensors import FrameTransformerCfg
from omni.isaac.orbit.sensors.frame_transformer.frame_transformer_cfg import OffsetCfg
from omni.isaac.orbit.utils.assets import ISAAC_NUCLEUS_DIR, NVIDIA_NUCLEUS_DIR



"""
Environment configuration
"""
@configclass
class UR5eShelfEnvCfg(ShelfEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # switch robot to ur5e
        self.scene.robot = UR5e_2f85_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        # Set actions for the specific robot type (UR5e with Gripper)
        self.actions.arm_action = mdp.JointPositionActionCfg(
            asset_name="robot", 
            joint_names=["shoulder_pan_joint",
                        "shoulder_lift_joint",
                        "elbow_joint",
                        "wrist_1_joint",
                        "wrist_2_joint",
                        "wrist_3_joint"], 
            scale=0.5, 
            use_default_offset=True
        )
        self.actions.gripper_aciton = mdp.BinaryJointPositionActionCfg(
            asset_name="robot",
            joint_names=["left_outer_knuckle_joint", "right_outer_knuckle_joint"],
            open_command_expr={"left_outer_knuckle_joint": 0.0, "right_outer_knuckle_joint": 0.0},
            close_command_expr={"left_outer_knuckle_joint": 0.4, "right_outer_knuckle_joint": -0.4},
        )
                
        # Listens to the required transforms
        marker_cfg = FRAME_MARKER_CFG.copy()
        marker_cfg.markers["frame"].scale = (0.1, 0.1, 0.1)
        marker_cfg.prim_path = "/Visual/FrameTransformer"
        self.scene.ee_frame = FrameTransformerCfg(
            prim_path="{ENV_REGEX_NS}/Robot/base_link",
            debug_vis=True,
            visualizer_cfg=marker_cfg,
            target_frames=[FrameTransformerCfg.FrameCfg(
                            prim_path="{ENV_REGEX_NS}/Robot/robotiq_arg2f_base_link",
                            name="end_effector",
                            offset=OffsetCfg(
                                pos=[0.0, 0.0, 0.1770],
                            ),
                ),
            ],
        )

        


        self.rewards.grasp_target.params["open_joint_pos"] = 0.0
        self.rewards.grasp_target.params["asset_cfg"].joint_names = ["left_outer_knuckle_joint", "right_outer_knuckle_joint"]

@configclass
class UR5eShelfEnvCfg_PLAY(UR5eShelfEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # make a smaller scene for play
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # disable randomization for play
        self.observations.policy.enable_corruption = False