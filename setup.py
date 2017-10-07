import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-messenger',
    version='0.04',
    packages=['msgr', 'msgr.utils', 'msgr.management', 'msgr.management.commands'],
    include_package_data=True,
    description='A simple Django app to interact with social-media messengers',
    long_description=README,
    url='https://reliscore.com/',
    author='Manish (at) ReliScore.com',
    author_email='manish@reliscore.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',        
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
