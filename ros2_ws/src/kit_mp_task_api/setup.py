import os
from glob import glob
from setuptools import find_packages, setup

package_name = "kit_mp_task_api"

setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "tasks"), glob("tasks/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Jakob Thumm",
    maintainer_email="jakob.thumm@kit.edu",
    description="Task definitions and the student-facing planning API.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "run_task = kit_mp_task_api.run_task:main",
        ],
    },
)
