#!/usr/bin/env python

import setuptools as s

with open("README.md", "r") as fh:
    long_description = fh.read()

s.setup(
    name="pytest-track",
    version="0.1.2",
    author="Virtosu Bogdan",
    author_email="virtosu.bogdan@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/virtosubogdan/pytest-track",
    packages=s.find_packages(),
    include_package_data=True,
    install_requires=["mando==0.6.4", "atlassian-python-api==1.11.19", "pytest>=3.0", "beautifulsoup4", "tabulate"],
    entry_points={"pytest11": ["track = pytest_track.plugin"]},
    license="MIT",
    keywords="pytest report",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
