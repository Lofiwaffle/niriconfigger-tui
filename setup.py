#!/usr/bin/env python3
"""Setup script for NiriConfig GUI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="niri-config-gui",
    version="1.0.0",
    author="Your Name",
    description="GUI configuration manager for Niri Wayland compositor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/niri-config-gui",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 :: Qt",
        "Intended Audience :: Developers",
        "Topic :: Desktop Environment :: Window Managers",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.0",
        "kdl-py>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "niri-config-gui=src.main:main",
        ],
    },
)
