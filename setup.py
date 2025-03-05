"""Setup configuration for the package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.in", "r", encoding="utf-8") as f:
    REQUIREMENTS = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("requirements-dev.in", "r", encoding="utf-8") as f:
    DEV_REQUIREMENTS = [
        line.strip() for line in f 
        if line.strip() and not line.startswith("#") and not line.startswith("-c")
    ]

setup(
    name="finanalyzer",
    version="0.1.0",
    author="jerosa",
    description="A comprehensive tool for analyzing and visualizing financial data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jerosa/settle-up-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": DEV_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "finanalyzer=finanalyzer.cli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "finanalyzer": [
            "web/static/*",
            "web/templates/*",
        ],
    },
) 
