from setuptools import setup

version = "1.0.6"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="jsonfeed-wrapper",
    version=version,
    packages=["jsonfeed_wrapper"],
    # metadata for upload to PyPI
    author="Lukas Schwab",
    author_email="lukas.schwab@gmail.com",
    description="Python package for serving JSON feeds processed from fetched sites.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="json feed jsonfeed",
    url="https://github.com/lukasschwab/jsonfeed-wrapper",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
