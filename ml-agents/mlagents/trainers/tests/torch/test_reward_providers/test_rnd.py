import numpy as np
import pytest
from mlagents.torch_utils import torch
from mlagents.trainers.torch.components.reward_providers import (
    RNDRewardProvider,
    create_reward_provider,
)
from mlagents_envs.base_env import BehaviorSpec, ActionSpec
from mlagents.trainers.settings import RNDSettings, RewardSignalType
from mlagents.trainers.tests.torch.test_reward_providers.utils import (
    create_agent_buffer,
)
from mlagents.trainers.tests.dummy_config import create_observation_specs_with_shapes


SEED = [42]

ACTIONSPEC_CONTINUOUS = ActionSpec.create_continuous(5)
ACTIONSPEC_TWODISCRETE = ActionSpec.create_discrete((2, 3))
ACTIONSPEC_DISCRETE = ActionSpec.create_discrete((2,))


@pytest.mark.parametrize(
    "behavior_spec",
    [
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,)]), ACTIONSPEC_CONTINUOUS
        ),
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,)]), ACTIONSPEC_TWODISCRETE
        ),
    ],
)
def test_construction(behavior_spec: BehaviorSpec) -> None:
    curiosity_settings = RNDSettings(32, 0.01)
    curiosity_settings.strength = 0.1
    curiosity_rp = RNDRewardProvider(behavior_spec, curiosity_settings)
    assert curiosity_rp.strength == 0.1
    assert curiosity_rp.name == "RND"


@pytest.mark.parametrize(
    "behavior_spec",
    [
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,)]), ACTIONSPEC_CONTINUOUS
        ),
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,), (64, 66, 3), (84, 86, 1)]),
            ACTIONSPEC_CONTINUOUS,
        ),
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,), (64, 66, 1)]),
            ACTIONSPEC_TWODISCRETE,
        ),
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,)]), ACTIONSPEC_DISCRETE
        ),
    ],
)
def test_factory(behavior_spec: BehaviorSpec) -> None:
    curiosity_settings = RNDSettings(32, 0.01)
    curiosity_rp = create_reward_provider(
        RewardSignalType.RND, behavior_spec, curiosity_settings
    )
    assert curiosity_rp.name == "RND"


@pytest.mark.parametrize("seed", SEED)
@pytest.mark.parametrize(
    "behavior_spec",
    [
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,), (64, 66, 3), (24, 26, 1)]),
            ACTIONSPEC_CONTINUOUS,
        ),
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,)]), ACTIONSPEC_TWODISCRETE
        ),
        BehaviorSpec(
            create_observation_specs_with_shapes([(10,)]), ACTIONSPEC_DISCRETE
        ),
    ],
)
def test_reward_decreases(behavior_spec: BehaviorSpec, seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    rnd_settings = RNDSettings(32, 0.01)
    rnd_rp = RNDRewardProvider(behavior_spec, rnd_settings)
    buffer = create_agent_buffer(behavior_spec, 5)
    rnd_rp.update(buffer)
    reward_old = rnd_rp.evaluate(buffer)[0]
    for _ in range(100):
        rnd_rp.update(buffer)
        reward_new = rnd_rp.evaluate(buffer)[0]
    assert reward_new < reward_old
