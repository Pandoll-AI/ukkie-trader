import os
import re
from setuptools import setup, find_packages

def get_version():
    init_py = os.path.join(os.path.dirname(__file__), "src", "ukkie_trader", "__init__.py")
    with open(init_py, "r") as f:
        return re.search(r'__version__ = ["\']([^"\']+)["\']', f.read()).group(1)

setup(
    name="ukkie-trader",
    version=get_version(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer[all]",
        "rich",
        "pandas",
        "numpy",
        "pydantic",
        "ccxt",
    ],
    entry_points={
        "console_scripts": [
            "ukkie=ukkie_trader.cli.app:app",
        ],
    },
)
