from setuptools import find_packages, setup
import os

DIR_DATA='./'

F_VERSION=DIR_DATA+os.path.sep+'version.txt'

with open(F_VERSION, 'r') as f:
    version=f.read()
    version=version.strip()

setup(
    name='lifelogserver',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'waitress>=1.4.4', 'matplotlib>=3.2.1', 'numpy>=1.18.5'
    ],
    extras_require={"test": ["pytest", "coverage"]},
)
