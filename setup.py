from setuptools import setup, find_packages
from lacli import __version__

setup(version=__version__,
      name="lacli",
      author="Konstantinos Koukopoulos",
      author_email='kk@longaccess.com',
      description="The Long Access client",
      long_description=open('README').read(),
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
      package_data={'lacli': ['data/certificate.html']}
      )
