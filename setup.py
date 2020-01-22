import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wimblepong",
    version="1.0",
    author="Karol Arndt, Oliver Struckmeier",
    author_email="karol.arndt@aalto.fi, oliver.struckmeier@aalto.fi",
    description="A two player gym environment similar to the official single player Pong-v0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/aalto-intelligent-robotics/wimblepong",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
