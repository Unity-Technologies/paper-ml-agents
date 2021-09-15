import pytest

import numpy as np

from mlagents.trainers.ghost.trainer import GhostTrainer
from mlagents.trainers.ghost.controller import GhostController
from mlagents.trainers.behavior_id_utils import BehaviorIdentifiers
from mlagents.trainers.ppo.trainer import PPOTrainer
from mlagents.trainers.agent_processor import AgentManagerQueue
from mlagents.trainers.buffer import BufferKey, RewardSignalUtil
from mlagents.trainers.tests import mock_brain as mb
from mlagents.trainers.tests.mock_brain import copy_buffer_fields
from mlagents.trainers.tests.test_trajectory import make_fake_trajectory
from mlagents.trainers.settings import TrainerSettings, SelfPlaySettings
from mlagents.trainers.tests.dummy_config import create_observation_specs_with_shapes


@pytest.fixture
def dummy_config():
    return TrainerSettings(self_play=SelfPlaySettings())


VECTOR_ACTION_SPACE = 1
VECTOR_OBS_SPACE = 8
DISCRETE_ACTION_SPACE = [3, 3, 3, 2]
BUFFER_INIT_SAMPLES = 10241
NUM_AGENTS = 12


@pytest.mark.parametrize("use_discrete", [True, False])
def test_load_and_set(dummy_config, use_discrete):
    mock_specs = mb.setup_test_behavior_specs(
        use_discrete,
        False,
        vector_action_space=DISCRETE_ACTION_SPACE
        if use_discrete
        else VECTOR_ACTION_SPACE,
        vector_obs_space=VECTOR_OBS_SPACE,
    )

    trainer_params = dummy_config
    trainer = PPOTrainer("test", 0, trainer_params, True, False, 0, "0")
    trainer.seed = 1
    policy = trainer.create_policy("test", mock_specs)
    trainer.seed = 20  # otherwise graphs are the same
    to_load_policy = trainer.create_policy("test", mock_specs)

    weights = policy.get_weights()
    load_weights = to_load_policy.get_weights()
    try:
        for w, lw in zip(weights, load_weights):
            np.testing.assert_array_equal(w, lw)
    except AssertionError:
        pass

    to_load_policy.load_weights(weights)
    load_weights = to_load_policy.get_weights()

    for w, lw in zip(weights, load_weights):
        np.testing.assert_array_equal(w, lw)


def test_resume(dummy_config, tmp_path):
    mock_specs = mb.setup_test_behavior_specs(
        True, False, vector_action_space=[2], vector_obs_space=1
    )
    behavior_id_team0 = "test_brain?team=0"
    behavior_id_team1 = "test_brain?team=1"
    brain_name = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team0).brain_name
    tmp_path = tmp_path.as_posix()
    ppo_trainer = PPOTrainer(brain_name, 0, dummy_config, True, False, 0, tmp_path)
    controller = GhostController(100)
    trainer = GhostTrainer(
        ppo_trainer, brain_name, controller, 0, dummy_config, True, tmp_path
    )

    parsed_behavior_id0 = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team0)
    policy = trainer.create_policy(parsed_behavior_id0, mock_specs)
    trainer.add_policy(parsed_behavior_id0, policy)

    parsed_behavior_id1 = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team1)
    policy = trainer.create_policy(parsed_behavior_id1, mock_specs)
    trainer.add_policy(parsed_behavior_id1, policy)

    trainer.save_model()

    # Make a new trainer, check that the policies are the same
    ppo_trainer2 = PPOTrainer(brain_name, 0, dummy_config, True, True, 0, tmp_path)
    trainer2 = GhostTrainer(
        ppo_trainer2, brain_name, controller, 0, dummy_config, True, tmp_path
    )
    policy = trainer2.create_policy(parsed_behavior_id0, mock_specs)
    trainer2.add_policy(parsed_behavior_id0, policy)

    policy = trainer2.create_policy(parsed_behavior_id1, mock_specs)
    trainer2.add_policy(parsed_behavior_id1, policy)

    trainer1_policy = trainer.get_policy(parsed_behavior_id1.behavior_id)
    trainer2_policy = trainer2.get_policy(parsed_behavior_id1.behavior_id)
    weights = trainer1_policy.get_weights()
    weights2 = trainer2_policy.get_weights()

    for w, lw in zip(weights, weights2):
        np.testing.assert_array_equal(w, lw)


def test_process_trajectory(dummy_config):
    mock_specs = mb.setup_test_behavior_specs(
        True, False, vector_action_space=[2], vector_obs_space=1
    )
    behavior_id_team0 = "test_brain?team=0"
    behavior_id_team1 = "test_brain?team=1"
    brain_name = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team0).brain_name

    ppo_trainer = PPOTrainer(brain_name, 0, dummy_config, True, False, 0, "0")
    controller = GhostController(100)
    trainer = GhostTrainer(
        ppo_trainer, brain_name, controller, 0, dummy_config, True, "0"
    )

    # first policy encountered becomes policy trained by wrapped PPO
    parsed_behavior_id0 = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team0)
    policy = trainer.create_policy(parsed_behavior_id0, mock_specs)
    trainer.add_policy(parsed_behavior_id0, policy)
    trajectory_queue0 = AgentManagerQueue(behavior_id_team0)
    trainer.subscribe_trajectory_queue(trajectory_queue0)

    # Ghost trainer should ignore this queue because off policy
    parsed_behavior_id1 = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team1)
    policy = trainer.create_policy(parsed_behavior_id1, mock_specs)
    trainer.add_policy(parsed_behavior_id1, policy)
    trajectory_queue1 = AgentManagerQueue(behavior_id_team1)
    trainer.subscribe_trajectory_queue(trajectory_queue1)

    time_horizon = 15
    trajectory = make_fake_trajectory(
        length=time_horizon,
        max_step_complete=True,
        observation_specs=create_observation_specs_with_shapes([(1,)]),
        action_spec=mock_specs.action_spec,
    )
    trajectory_queue0.put(trajectory)
    trainer.advance()

    # Check that trainer put trajectory in update buffer
    assert trainer.trainer.update_buffer.num_experiences == 15

    trajectory_queue1.put(trajectory)
    trainer.advance()

    # Check that ghost trainer ignored off policy queue
    assert trainer.trainer.update_buffer.num_experiences == 15
    # Check that it emptied the queue
    assert trajectory_queue1.empty()


def test_publish_queue(dummy_config):
    mock_specs = mb.setup_test_behavior_specs(
        True, False, vector_action_space=[1], vector_obs_space=8
    )

    behavior_id_team0 = "test_brain?team=0"
    behavior_id_team1 = "test_brain?team=1"

    parsed_behavior_id0 = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team0)

    brain_name = parsed_behavior_id0.brain_name

    ppo_trainer = PPOTrainer(brain_name, 0, dummy_config, True, False, 0, "0")
    controller = GhostController(100)
    trainer = GhostTrainer(
        ppo_trainer, brain_name, controller, 0, dummy_config, True, "0"
    )

    # First policy encountered becomes policy trained by wrapped PPO
    # This queue should remain empty after swap snapshot
    policy = trainer.create_policy(parsed_behavior_id0, mock_specs)
    trainer.add_policy(parsed_behavior_id0, policy)
    policy_queue0 = AgentManagerQueue(behavior_id_team0)
    trainer.publish_policy_queue(policy_queue0)

    # Ghost trainer should use this queue for ghost policy swap
    parsed_behavior_id1 = BehaviorIdentifiers.from_name_behavior_id(behavior_id_team1)
    policy = trainer.create_policy(parsed_behavior_id1, mock_specs)
    trainer.add_policy(parsed_behavior_id1, policy)
    policy_queue1 = AgentManagerQueue(behavior_id_team1)
    trainer.publish_policy_queue(policy_queue1)

    # check ghost trainer swap pushes to ghost queue and not trainer
    assert policy_queue0.empty() and policy_queue1.empty()
    trainer._swap_snapshots()
    assert policy_queue0.empty() and not policy_queue1.empty()
    # clear
    policy_queue1.get_nowait()

    buffer = mb.simulate_rollout(BUFFER_INIT_SAMPLES, mock_specs)
    # Mock out reward signal eval
    copy_buffer_fields(
        buffer,
        src_key=BufferKey.ENVIRONMENT_REWARDS,
        dst_keys=[
            BufferKey.ADVANTAGES,
            RewardSignalUtil.rewards_key("extrinsic"),
            RewardSignalUtil.returns_key("extrinsic"),
            RewardSignalUtil.value_estimates_key("extrinsic"),
            RewardSignalUtil.rewards_key("curiosity"),
            RewardSignalUtil.returns_key("curiosity"),
            RewardSignalUtil.value_estimates_key("curiosity"),
        ],
    )

    trainer.trainer.update_buffer = buffer

    # when ghost trainer advance and wrapped trainer buffers full
    # the wrapped trainer pushes updated policy to correct queue
    assert policy_queue0.empty() and policy_queue1.empty()
    trainer.advance()
    assert not policy_queue0.empty() and policy_queue1.empty()


if __name__ == "__main__":
    pytest.main()
