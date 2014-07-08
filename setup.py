#!/usr/bin/env python

from distutils.core import setup

setup(name='Directly',
      version='1.0',
      description='ExtDirect python implementation for Django-powered apps.',
      author='Alex Mannhold',
      author_email='EvilDwarf@gmx.net',
      url='https://github.com/NinjaDero/Directly',
      download_url='https://github.com/NinjaDero/Directly/archive/master.zip',
      packages=['Directly'],
      package_dir={'Directly':'Directly'},
      package_data={'Directly':['LICENCE']},
      classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Web Environment',
              'Intended Audience :: Developers',
              'Programming Language :: Python',
              ],
)
