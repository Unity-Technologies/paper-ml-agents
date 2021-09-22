from typing import Optional, Any
from mlagents_envs.registry import UnityEnvRegistry
from mlagents_envs.base_env import BaseEnv
from mlagents_envs.registry.remote_registry_entry import RemoteRegistryEntry
from mlagents_envs.registry.base_registry_entry import BaseRegistryEntry
from mapoca.particles_env import ParticlesEnvironment

mapoca_registry = UnityEnvRegistry()

mapoca_registry.register(
    RemoteRegistryEntry(
        "BatonPass",
        15,
        "The baton pass environment",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/linux/Startup.zip",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/darwin/Startup.zip",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/win/Startup.zip",
        ["--mlagents-scene-name", "Assets/ML-Agents/Examples/BatonPass/Scenes/BatonPass.unity"]
    ))
mapoca_registry.register(
    RemoteRegistryEntry(
        "DungeonEscape",
        1,
        "Thedungeon escape environment (hard version)",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/linux/Startup.zip",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/darwin/Startup.zip",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/win/Startup.zip",
        ["--mlagents-scene-name", "Assets/ML-Agents/Examples/DungeonEscape/Scenes/DungeonEscapeHard.unity"]
    )
)

mapoca_registry.register(
    RemoteRegistryEntry(
        "PushBlockColab",
        9,
        "The push block colab environment",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/linux/Startup.zip",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/darwin/Startup.zip",
        "https://storage.googleapis.com/mlagents-test-environments/ma-poca/win/Startup.zip",
        ["--mlagents-scene-name", "Assets/ML-Agents/Examples/PushBlock/Scenes/PushBlockCollab.unity"]
    )
)

class ParticleEnvEntry(BaseRegistryEntry):
    def __init__(
        self,
        identifier: str,
        expected_reward: Optional[float],
        description: Optional[str],
    ):
        super().__init__(identifier, expected_reward, description)

    def make(self, **kwargs: Any) -> BaseEnv:
        return ParticlesEnvironment(worker_id = kwargs["worker_id"])

mapoca_registry.register(
    ParticleEnvEntry(
        "ParticlesEnv",
        - 160,
        "The particles environment from https://github.com/openai/multiagent-particle-envs"
    )
)
