from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'slackclient',
    'requests',
    'BeautifulSoup4',
    'apscheduler',
    'icalendar',
    'pytz',
    'python-dateutil',
    'google-api-python-client'
]

test_requires = [
    'pytest',
]

setup(
    name='uqcsbot',
    version='0.0.1',
    description='UQCSbot is a chat bot built in python for use on our UQCS Slack Team',
    long_description=long_description,
    url='https://github.com/UQComputingSociety/uqcsbot',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='slack async lightweight',
    packages=find_packages(),
    install_requires=install_requires,
    test_requires=test_requires,
    extras_require={
        'test': test_requires,
    }
)
