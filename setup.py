""" Setup file. """

from setuptools import find_packages, setup

with open("README.rst", "r") as readme_file:
    README = readme_file.read()

exec(open("src/matching/version.py", "r").read())

setup(
    name="matching",
    version=__version__,
    description="A package for solving matching games.",
    long_description=README,
    url="https://github.com/daffidwilde/matching",
    author="Henry Wilde",
    author_email="henrydavidwilde@gmail.com",
    license="MIT",
    keywords=["game-theory gale-shapley matching-games"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.5",
    tests_require=["pytest", "hypothesis", "numpy"],
)
