import os
import sys
import argparse

from .yamato_utils import get_base_path, run_standalone_build


def main(scene_path, build_target):
    base_path = get_base_path()
    print(f"Running in base path {base_path}")

    executable_name = "testPlayer"
    if scene_path is not None:
        executable_name = os.path.splitext(scene_path)[0]  # Remove extension
        executable_name = executable_name.split("/")[-1]
        executable_name = "testPlayer-" + executable_name
    print(f"Executable name {executable_name}")

    returncode = run_standalone_build(
        base_path,
        output_path=executable_name,
        scene_path=scene_path,
        build_target=build_target,
        log_output_path=None,  # Log to stdout so we get timestamps on the logs
    )

    if returncode == 0:
        print("Test run SUCCEEDED!")
    else:
        print("Test run FAILED!")

    sys.exit(returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", default=None)
    parser.add_argument(
        "--build-target", default="mac", choices=["mac", "linux", "ios", "webgl"]
    )
    args = parser.parse_args()
    main(args.scene, args.build_target)
