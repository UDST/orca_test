from setuptools import setup, find_packages

setup(
    name='orca_test',
    version='0.1',
    description='Assertions for testing the characteristics of orca tables and columns',
    author='UrbanSim Inc.',
    author_email='info@urbansim.com',
    url='https://github.com/urbansim/orca_test',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'numpy >= 1.0',
        'pandas >= 0.12',
        'orca >= 1.3.0'
    ]
)
