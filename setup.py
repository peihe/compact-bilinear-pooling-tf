#coding=utf8

from setuptools import setup, find_packages, Distribution

class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True

setup(
    name="count_sketch",
    version="0.0.1",
    packages = find_packages(),
    include_package_data=True,
    distclass=BinaryDistribution
)


