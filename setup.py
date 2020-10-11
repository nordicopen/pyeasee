"""Setup script for easee"""

import os.path
from setuptools import setup

# This call to setup() does all the work
setup(
    name="pyeasee",
    version="0.7.21",
    description="Easee EV charger API library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fondberg/pyeasee",
    author="Niklas Fondberg",
    author_email="niklas.fondberg@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["pyeasee"],
    include_package_data=True,
    install_requires=["aiohttp"],
    entry_points={"console_scripts": ["pyeasee=pyeasee.__main__:main"]},
)
