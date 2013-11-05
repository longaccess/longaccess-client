from setuptools import setup, find_packages
from lacli import __version__

try:
    import pandoc
    pandoc.core.PANDOC_PATH = 'pandoc'
    readme = pandoc.Document()
    readme.markdown = open('README.md').read()
    description = readme.rst
except (IOError, ImportError):
    description = 'This is the prototype client program' + \
        'for interacting with the Longaccess service.'

setup(version=__version__,
      name="lacli",
      author="Konstantinos Koukopoulos",
      author_email='kk@longaccess.com',
      description="The Long Access client",
      long_description=description,
      url='http://github.com/longaccess/longaccess-client/',
      license='Apache',
      packages=find_packages(exclude=['features*', '*.t']),
      install_requires=['boto>=2.13.2', 'python-dateutil', 'filechunkio',
                        'docopt', 'progressbar', 'logutils', 'requests',
                        'unidecode', 'pycrypto', 'pyaml'],
      tests_require=['testtools'],
      test_suite="lacli.t",
      entry_points="""
      [console_scripts]
      lacli = lacli.main:main
      ladec = lacli.cipher.dec:main
      """,
      package_data={'lacli': ['data/certificate.html']},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Information Technology',
          'Natural Language :: English',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Archiving',
          'Topic :: Utilities',
      ],
      )
