"""Setup script for Settle Up Analyzer."""
from setuptools import setup, find_packages

setup(
    name="settle-up-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dash==2.14.2",
        "dash-bootstrap-components==1.5.0",
        "plotly==5.18.0",
        "pandas==2.1.4",
        "python-dotenv==1.0.0",
        "numpy==1.24.4",
        "seaborn==0.12.2",
        "matplotlib==3.7.2",
    ],
    python_requires=">=3.10",
) 
