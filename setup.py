from setuptools import setup

with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

setup(
    name='uqcsbot',
    version='1.0',
    description='Bot for UQCS Slack',
    author='UQ Computing Society',
    packages=['uqcsbot'],
    install_requires=REQUIRED)
