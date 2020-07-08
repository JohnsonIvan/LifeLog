from setuptools import find_packages, setup

setup(
    name='lifelogserver',
    version='0.7.0a0.dev2',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'waitress>=1.4.4', 'matplotlib>=3.2.1', 'numpy>=1.18.5'
    ],
    extras_require={"test": ["pytest", "coverage"]},
)
