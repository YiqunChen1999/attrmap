"""
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="attrmap",
    version="0.0.1",
    author="Yiqun Chen",
    author_email="yiqunchen1999@gmail.com",
    description="Attribute Mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yiqunchen1999/attrmap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)