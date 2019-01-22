""" Setup file. """

from setuptools import setup, find_packages

with open("README.rst", "r") as readme_file:
    README = readme_file.read()

setup(
    name="matching",
    version="1.0",
    description="A package for solving matching games.",
    long_description=README,
    url="https://github.com/daffidwilde/matching",
    author="Henry Wilde",
    author_email="henrydavidwilde@gmail.com",
    license="MIT",
    keywords=["game-theory gale-shapley matching-games"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    tests_require=["pytest", "numpy"],
)
