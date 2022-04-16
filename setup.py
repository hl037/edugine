#!/usr/bin/env python
import sys

from setuptools import setup, find_packages


def read_file(name):
    """
    Read file content
    """
    f = open(name)
    try:
        return f.read()
    except IOError:
        print("could not read %r" % name)
        f.close()

LONG_DESC = read_file('README.md') + '\n\n' + read_file('HISTORY.md')

EXTRAS = {}

if sys.version_info < (3,):
    EXTRAS['use_2to3'] = True

setup(
    name='edugine',
    version='0.1.dev4',
    description='',
    long_description=LONG_DESC,
    long_description_content_type='text/markdown',
    author='Léo Flaventin Hauchecorne',
    author_email='hl037.prog@gmail.com',
    url='https://github.com/hl037/edugine',
    license='GPLv3',
    packages=find_packages(),
    test_suite=None,
    include_package_data=True,
    zip_safe=False,
    install_requires=['numpy', 'pyglet', 'icecream', 'scipy'],
    extras_require=None,
    #entry_points={
    #  'console_scripts':[
    #    'name=module.submodule:function',
    #  ]
    #},
    #package_data={
    #  'module' : ['module/path/to/data', 'path/to/glob/*'],
    #},
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Education',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Games/Entertainment',
      'Topic :: Games/Entertainment :: Arcade',
      'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    **EXTRAS
)
