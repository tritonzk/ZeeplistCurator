from setuptools import setup

setup(
    name='console',
    version='0.1.0',
    py_modules=['Console_new'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'yourscript = yourscript:cli',
        ],
    },
)
