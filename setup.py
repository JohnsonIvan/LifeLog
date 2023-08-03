from setuptools import find_packages, setup

setup(
    name='lifelogserver',
    version='0.7.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'waitress>=2.1.2', 'matplotlib>=3.2.1', 'numpy>=1.18.5'
    ],
    extras_require={"test": ["pytest", "coverage"]},
)
