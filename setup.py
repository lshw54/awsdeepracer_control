import setuptools

with open("README.md") as f:
    README = f.read()

setuptools.setup(
    author="lshw54",
    author_email="lshw.5454@gmail.com",
    name="awsdeepracer_control",
    license="MIT",
    description="awsdeepracer_control is a rewrite python package for control the DeepRacer vehicle via HTTP API.",
    version="0.2.0",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lshw54/awsdeepracer_control",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "beautifulsoup4>=4.8.2",
        "bs4>=0.0.1",
        "lxml>=4.4.2",
        "PyYAML>=5.3",
        "requests>=2.22.0",
        "requests-toolbelt>=0.9.1",
        "urllib3>=1.25.8",
    ],
)