from setuptools  import setup

setup(
    name='cananalyze',
    version='0.1.0',
    author='Renault & Thales',
    packages=['cananalyze'],
    include_package_data=True,
    package_data={'cananalyze': ['komodo.so',]},
    license='LICENSE.txt',
    description='framework to interact with automotive protocols like CAN/ISOTP/UDS and emulate ECU',
    long_description=open('README.md').read(),
    install_requires=[
        "python-can==4.0.0",
        "sphinx-rtd-theme==1.0.0",
    ],
)
