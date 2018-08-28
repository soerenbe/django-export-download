# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

with open('README.md') as file:
    long_description = file.read()

setup(
    name='django-export-download',
    packages=find_packages(exclude=['build', 'demo']),
    version='0.2.3',
    description='A Django library that adds a ListView Mixin for downloading a list in different file formats',
    long_description=long_description,
    author='Sören Berger',
    author_email='soeren.berger@u1337.de',
    url='https://github.com/soerenbe/django-export-download',
    download_url='https://github.com/soerenbe/django-export-download/',
    keywords=['django', 'nagios', 'icinga'],
    install_requires=["Django>=1.11", "django-import-export>=1.0"],
    license='GPL-3',
    package_data={
        '': ['templates/export_download/*.html'],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
)
