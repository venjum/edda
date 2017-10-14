from setuptools import setup, find_packages
import os.path

version = open(os.path.join(os.path.split(__file__)[0], "VERSION"), "rt").read().strip()

setup(
    name="edda",
    version=version,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['bluesound', 'python-yr'],
    description='Kivy application for Bluesound amplifiers',
    long_description=open('README.md').read(),
    author='Kai André Venjum',
    author_email='kai.andre@venjum.com',
    url='https://github.com/venjum/edda')
