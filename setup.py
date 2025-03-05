"""Setup configuration for the Settle Up Analyzer package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies required for both CLI and web app
CORE_REQUIREMENTS = [
    "pandas>=1.4.0",
    "numpy>=1.21.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.11.0",
    "python-dotenv>=0.19.0",
    "openpyxl>=3.0.0",  # For Excel support
    "xlrd>=2.0.0",      # For Excel support
]

# Additional requirements for CLI
CLI_REQUIREMENTS = [
    "click>=8.0.0",
] + CORE_REQUIREMENTS

# Additional requirements for web app
WEB_REQUIREMENTS = [
    "flask>=2.0.0",
    "dash>=2.14.0",
    "dash-bootstrap-components>=1.5.0",
    "plotly>=5.18.0",
] + CORE_REQUIREMENTS

setup(
    name="settle-up-analyzer",
    version="0.1.0",
    author="jerosa",
    description="A tool for analyzing Settle Up expense data",
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
    install_requires=CORE_REQUIREMENTS,
    extras_require={
        "cli": CLI_REQUIREMENTS,
        "web": WEB_REQUIREMENTS,
        "all": list(set(CLI_REQUIREMENTS + WEB_REQUIREMENTS)),
    },
    entry_points={
        "console_scripts": [
            "settle-up=settle_up.cli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "settle_up": [
            "web/static/*",
            "web/templates/*",
        ],
    },
) 
