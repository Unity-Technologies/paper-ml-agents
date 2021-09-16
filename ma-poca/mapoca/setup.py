import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install
from mapoca.plugins import ML_AGENTS_STATS_WRITER
import mapoca.trainers
VERSION = mapoca.trainers.__version__

here = os.path.abspath(os.path.dirname(__file__))


# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mapoca",
    version=VERSION,
    description="Unity Machine Learning Agents, MA-POCA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/Unity-Technologies/paper-ml-agents",
    author="Unity Technologies",
    author_email="ML-Agents@unity3d.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    # find_namespace_packages will recurse through the directories and find all the packages
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    zip_safe=False,
    install_requires=[
        # Test-only dependencies should go in test_requirements.txt, not here.
        "grpcio>=1.11.0",
        "h5py>=2.9.0",
        f"mlagents_envs==0.27.0",
        "numpy>=1.13.3,<2.0",
        "Pillow>=4.2.1",
        "protobuf>=3.6",
        "pyyaml>=3.1.0",
        # Windows ver. of PyTorch doesn't work from PyPi. Installation:
        # https://github.com/Unity-Technologies/ml-agents/blob/release_18_docs/docs/Installation.md#windows-installing-pytorch
        # Torch only working on python 3.9 for 1.8.0 and above. Details see:
        # https://github.com/pytorch/pytorch/issues/50014
        "torch>=1.8.0,<1.9.0;(platform_system!='Windows' and python_version>='3.9')",
        "torch>=1.6.0,<1.9.0;(platform_system!='Windows' and python_version<'3.9')",
        "tensorboard>=1.15",
        # cattrs 1.1.0 dropped support for python 3.6, but 1.0.0 doesn't work for python 3.9
        # Since there's no version that supports both, we have to draw the line somwehere.
        "cattrs<1.1.0; python_version<'3.8'",
        "cattrs>=1.1.0,<1.7; python_version>='3.8'",
        "attrs>=19.3.0",
        'pypiwin32==223;platform_system=="Windows"',
        "importlib_metadata; python_version<'3.8'",
        # Dependencies for particles envs
        "gym==0.10.5",
        "multiagent @ git+https://github.com/openai/multiagent-particle-envs.git",
    ],
    python_requires=">=3.6.1",
    entry_points={
        "console_scripts": [
            "mapoca-learn=mapoca.trainers.learn:main",
            "mapoca-run-experiment=mapoca.trainers.run_experiment:main",
        ],
        # Plugins - each plugin type should have an entry here for the default behavior
        ML_AGENTS_STATS_WRITER: [
            "default=mlagents.plugins.stats_writer:get_default_stats_writers"
        ],
    },
)
