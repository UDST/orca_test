# Install setuptools if not installed.
try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages


# read README as the long description
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='orca_test',
    version='0.1dev',
    description='Assertions for testing the characteristics of orca tables and columns',
    long_description=long_description,
    author='UrbanSim Inc.',
    author_email='info@urbansim.com',
    url='https://github.com/urbansim/orca_test',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'orca >= 1.3.0',
    ]
)
