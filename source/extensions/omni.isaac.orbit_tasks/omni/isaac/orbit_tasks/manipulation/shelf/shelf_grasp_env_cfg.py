from __future__ import annotations

from dataclasses import MISSING

import torch, numpy as np

import omni.isaac.orbit.sim as sim_utils
from omni.isaac.orbit.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from omni.isaac.orbit.envs import RLTaskEnvCfg
from omni.isaac.orbit.managers import CurriculumTermCfg as CurrTerm
from omni.isaac.orbit.managers import EventTermCfg as EventTerm
from omni.isaac.orbit.managers import ObservationGroupCfg as ObsGroup
from omni.isaac.orbit.managers import ObservationTermCfg as ObsTerm
from omni.isaac.orbit.managers import RewardTermCfg as RewTerm
from omni.isaac.orbit.managers import SceneEntityCfg
from omni.isaac.orbit.managers import TerminationTermCfg as DoneTerm
from omni.isaac.orbit.scene import InteractiveSceneCfg
from omni.isaac.orbit.sensors import CameraCfg, ContactSensorCfg, RayCasterCfg, patterns 
from omni.isaac.orbit.sensors.frame_transformer.frame_transformer_cfg import FrameTransformerCfg
from omni.isaac.orbit.sim.spawners.from_files.from_files_cfg import GroundPlaneCfg, UsdFileCfg
from omni.isaac.orbit.utils import configclass
from omni.isaac.orbit.utils.assets import ISAAC_NUCLEUS_DIR
from omni.isaac.orbit.sim.schemas.schemas_cfg import RigidBodyPropertiesCfg
from omni.isaac.orbit_tasks.manipulation.shelf import shelf_env_tools as tools

from . import mdp

@configclass
class ShelfSceneCfg(InteractiveSceneCfg):
    """
    Configuration for the unstructured scene with a robot and objects
    """

    # robots: will be populated by agent env cfg
    robot: ArticulationCfg = MISSING

    # end-effector sensor: will be populated by agent env cfg
    ee_frame: FrameTransformerCfg = MISSING

    # target object: will be popluated by agent env cfg
    object: RigidObjectCfg = MISSING



    # Shelf
    shelf = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Shelf",
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.5, 0, 0), rot=(1.0, 0.0, 0.0, 0.0)),
        spawn=UsdFileCfg(usd_path=f"/home/irol/KTH_dt/usd/Arena/Shelf.usd") # directory of the Shelf usd file
    )

    # Plane
    plane = AssetBaseCfg(
        prim_path="/World/GroundPlane",
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0, 0, -1.05)),
        spawn=GroundPlaneCfg(),
    )

    # Sensor


    # Lights
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=3000.0)
    )


@configclass
class CommandsCfg:
    """Command terms for the MDP."""
    """
    Set Goal pose of target object
    """

    object_pose = mdp.UniformPoseCommandCfg(
        asset_name="robot",
        body_name=MISSING,  # will be set by agent env cfg
        resampling_time_range=(10.0, 10.0),
        debug_vis=True,
        ranges=mdp.UniformPoseCommandCfg.Ranges(
            pos_x=(-0.25, 0.25), pos_y=(-0.6, -0.4), pos_z=(0.25, 0.5), roll=(0.0, 0.0), pitch=(0.0, 0.0), yaw=(0.0, 0.0)
        ),
    )

@configclass
class ActionsCfg:
    """
    Action spcifications for the MDP
    """

    # will be set by agent env cfg
    body_joint_pos: mdp.JointPositionActionCfg = MISSING
    # finger_joint_pos: mdp.BinaryJointPositionActionCfg = MISSING

@configclass
class ObservationsCfg:
    """
    Observation fpecifications for the MDP
    """

    @configclass
    class PolicyCfg(ObsGroup):
        """
        Observations for policy group
        """
        joint_pos = ObsTerm(func=mdp.joint_pos_rel)    
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        object_pose = ObsTerm(func=mdp.object_pose_in_robot_root_frame)
        target_object_position = ObsTerm(func=mdp.generated_commands, params={"command_name": "object_pose"})
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True
    

    # observation groups
    policy: PolicyCfg =  PolicyCfg()

@configclass
class EventCfg:
    """
    Configuration for events
    """

    reset_all = EventTerm(func=mdp.reset_scene_to_default, mode="reset")


@configclass
class RewardsCfg:
    """
    reward terms for the MDP
    """
    
    reaching_object = RewTerm(func=mdp.object_ee_distance, params={"std": 0.1}, weight=1.0)

    # grasping_object = RewTerm()

    object_goal_tracking = RewTerm(
        func=mdp.object_goal_distance,
        params={"std":0.3, "minimal_height": 0.06, "command_name": "object_pose"},
        weight=16.0,
    )

    object_goal_tracking_fine_grained = RewTerm(
        func=mdp.object_goal_distance,
        params={"std": 0.05, "minimal_height": 0.06, "command_name": "object_pose"},
        weight=5.0
    )

    # action penalty
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-1e-3)

    joint_vel = RewTerm(func=mdp.joint_vel_l2,
                        weight=-1e-4,
                        params={"asset_cfg": SceneEntityCfg("robot")},
                        )
    

@configclass
class TerminationsCfg:
    """
    Termination terms for the MDP
    """
    time_out = DoneTerm(func=mdp.time_out, time_out=True)

    object_dropping = DoneTerm(
        func=mdp.root_height_below_minimum, params={"minimum_height": -0.05, "asset_cfg": SceneEntityCfg("object")}
    )



@configclass
class CurriculumCfg:
    """
    Curriculum terms for the MDP
    """

    action_rate = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "action_rate", "weight": -1e-1, "num_steps": 10000}
    )

    joint_vel = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "joint_vel", "weight": -1e-1, "num_steps": 10000}
    )

    object_goal_tracking = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "object_goal_tracking", "weight": 30.0, "num_steps": 10000}
    )

    object_goal_tracking_fine_grained = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "object_goal_tracking_fine_grained", "weight": 10.0, "num_steps": 10000}
    )


@configclass
class ShelfGraspEnvCfg(RLTaskEnvCfg):
    """
    Configuration for the grasping environment
    """

    # Scene settings
    scene: ShelfSceneCfg = ShelfSceneCfg(num_envs=1024, env_spacing = 3)

    # Basic Settings
    observaitons: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()

    # MDP settings
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        """
        Post initialization
        """
        self.decimation = 2
        self.episode_length_s = 5.0
        # simulation settings
        self.sim.dt = 0.01

        self.sim.physx.bounce_threshold_velocity = 0.2
        self.sim.physx.bounce_threshold_velocity = 0.01
        self.sim.physx.gpu_found_lost_aggregate_pairs_capacity = 1024 * 1024 * 4 * 16
        self.sim.physx.gpu_total_aggregate_pairs_capacity = 16 * 1024 * 16
        self.sim.physx.gpu_max_rigid_patch_count = 5 * 2**20
        self.sim.physx.friction_correlation_distance = 0.00625     

        
