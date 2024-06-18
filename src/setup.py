from setuptools import find_packages, setup

setup(
    name="lifelogserver",
    version="0.8.0a0.dev0",  # TODO: de-dupe. Somehow. Or at least write a unit test?
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "waitress>=2.1.2", "matplotlib>=3.2.1", "numpy>=1.18.5"],
    extras_require={"test": ["pytest", "coverage"]},
    scripts=[
        "Scripts/launch.bash",
        "Scripts/flask.bash",
    ],
    entry_points={
        "console_scripts": [
            "lifelogserver = LifeLogServer.cli:main",
        ],
    },
)
