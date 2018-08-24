""" Setup file. """

from setuptools import setup, find_packages

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="matching",
    version="0.1.1",
    description="A package for solving matching games",
    long_description=readme,
    url="https://github.com/daffidwilde/matching",
    author="Henry Wilde",
    author_email="henrydavidwilde@gmail.com",
    license="MIT",
    keywords=["gametheory gale-shapley matchinggames"],
    packages=find_packages("src"),
    package_dir={"": "src"},
)
