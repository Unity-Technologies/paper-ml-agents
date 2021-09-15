import argparse

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import (
    EngineConfigurationChannel,
)


def test_run_environment(env_name):
    """
    Run the low-level API test using the specified environment
    :param env_name: Name of the Unity environment binary to launch
    """
    engine_configuration_channel = EngineConfigurationChannel()
    env = UnityEnvironment(
        file_name=env_name,
        side_channels=[engine_configuration_channel],
        no_graphics=True,
        additional_args=["-logFile", "-"],
    )

    try:
        # Reset the environment
        env.reset()

        # Set the default brain to work with
        group_name = list(env.behavior_specs.keys())[0]
        group_spec = env.behavior_specs[group_name]

        # Set the time scale of the engine
        engine_configuration_channel.set_configuration_parameters(time_scale=3.0)

        # Get the state of the agents
        decision_steps, terminal_steps = env.get_steps(group_name)

        # Examine the number of observations per Agent
        print("Number of observations : ", len(group_spec.observation_specs))

        for obs_spec in group_spec.observation_specs:
            # Make sure the name was set in the ObservationSpec
            assert bool(obs_spec.name) is True, f'obs_spec.name="{obs_spec.name}"'

        # Is there a visual observation ?
        vis_obs = any(
            len(obs_spec.shape) == 3 for obs_spec in group_spec.observation_specs
        )
        print("Is there a visual observation ?", vis_obs)

        # Examine the state space for the first observation for the first agent
        print(
            "First Agent observation looks like: \n{}".format(decision_steps.obs[0][0])
        )

        for _episode in range(10):
            env.reset()
            decision_steps, terminal_steps = env.get_steps(group_name)
            done = False
            episode_rewards = 0
            tracked_agent = -1
            while not done:
                action_tuple = group_spec.action_spec.random_action(len(decision_steps))
                if tracked_agent == -1 and len(decision_steps) >= 1:
                    tracked_agent = decision_steps.agent_id[0]
                env.set_actions(group_name, action_tuple)
                env.step()
                decision_steps, terminal_steps = env.get_steps(group_name)
                done = False
                if tracked_agent in decision_steps:
                    episode_rewards += decision_steps[tracked_agent].reward
                if tracked_agent in terminal_steps:
                    episode_rewards += terminal_steps[tracked_agent].reward
                    done = True
            print(f"Total reward this episode: {episode_rewards}")
    finally:
        env.close()


def test_closing(env_name):
    """
    Run the low-level API and close the environment
    :param env_name: Name of the Unity environment binary to launch
    """
    try:
        env1 = UnityEnvironment(
            file_name=env_name,
            base_port=5006,
            no_graphics=True,
            additional_args=["-logFile", "-"],
        )
        env1.close()
        env1 = UnityEnvironment(
            file_name=env_name,
            base_port=5006,
            no_graphics=True,
            additional_args=["-logFile", "-"],
        )
        env2 = UnityEnvironment(
            file_name=env_name,
            base_port=5007,
            no_graphics=True,
            additional_args=["-logFile", "-"],
        )
        env2.reset()
    finally:
        env1.close()
        env2.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="artifacts/testPlayer")
    args = parser.parse_args()
    test_run_environment(args.env)
    test_closing(args.env)
