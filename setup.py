from setuptools import setup, find_packages

setup(
    name="osiris",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "osiris=osiris.cli:main",  # Calls the `main()` function in cli.py
        ],
    },
)
