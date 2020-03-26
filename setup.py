"""A setuptools based setup module."""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='crontamer',
    version='1.0.1',
    description='A wrapper script for cron processes. Stops multiple process instances and gives a default timesout.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/cedadev/crontamer',
    # Author details
    author='Sam Pepler',
    author_email='sam.pepler@stfc.ac.uk',
    # Choose your license
    license='BSD',
    keywords='cron',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=["crontamer"],
    py_modules=["crontamer"],
    requires=["psutil", "docopt"],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'crontamer=crontamer:main',
        ],
    },
)