from setuptools import find_packages, setup

setup(
    name='lifelogserver',
    version='0.4.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
    extras_require={"test": ["pytest", "coverage"]},
)
