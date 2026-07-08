import os
from glob import glob
from setuptools import find_packages, setup

package_name = "kit_mp_benchmark"

setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Jakob Thumm",
    maintainer_email="jakob.thumm@kit.edu",
    description="Scoring and benchmarking harness for the KIT motion-planning exercise.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "scorer = kit_mp_benchmark.scorer:main",
            "benchmark_sweep = kit_mp_benchmark.run_benchmark:main",
            "leaderboard = kit_mp_benchmark.leaderboard:main",
            "plot = kit_mp_benchmark.plot:main",
        ],
    },
)
