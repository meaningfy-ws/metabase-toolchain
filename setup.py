import pathlib
import re

from pkg_resources import parse_requirements
from setuptools import setup, find_packages

kwargs = {}

with pathlib.Path('requirements.txt').open() as requirements:
    kwargs["install_requires"] = [str(requirement) for requirement in parse_requirements(requirements)]


def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


version = find_version("src/__init__.py")

with open("README.md", encoding="utf-8") as readme:
    long_description = readme.read()

packages = find_packages(exclude=("examples*", "test*"))

setup(
    name="metabase-toolchain",
    version=version,
    description="Metabase",
    author="Meaningfy",
    author_email="kaleanych@gmail.com",
    maintainer="Meaningfy Team",
    maintainer_email="contact@meaningfy.ws",
    url="https://github.com/meaningfy-ws/metabase-toolchain",
    license="Apache License 2.0",
    platforms=["any"],
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    entry_points={
        "console_scripts": [
            "export_metabase = src.migration.entrypoints.cli.cmd_export_metabase:main",
            "import_metabase = src.migration.entrypoints.cli.cmd_import_metabase:main"
        ],
    },
    include_package_data=True,
    **kwargs,
)
