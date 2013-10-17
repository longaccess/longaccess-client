from setuptools import setup
from lacli import __version__

setup(version=unicode(__version__),
      name="lacli",
      author="Konstantinos Koukopoulos",
      description="The Long Access client",
      long_description=open('README').read(),
      packages=['lacli', 'lacli.t', 'lacli.cipher'],
      install_requires=['boto', 'python-dateutil', 'filechunkio', 'docopt',
                        'progressbar', 'logutils', 'requests',
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
