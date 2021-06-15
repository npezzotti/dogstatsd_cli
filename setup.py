from setuptools import setup, find_packages

setup(
    name="dogstatsd-cli",
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': ['dogstatsd = dogstatsd_cli.cli:dogstatsd']
    },
)
