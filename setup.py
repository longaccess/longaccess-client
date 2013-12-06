from setuptools import setup, find_packages, Command
from setuptools.command.build_py import build_py as _build_py
from distutils.spawn import find_executable
from lacli import __version__
import os


class gen_thrift(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        thrift = find_executable('thrift')
        if thrift is not None:
            root = os.path.abspath(os.path.dirname(__file__))
            out = os.path.join(root, 'lacli', 'server', 'interface')
            self.mkpath(out)
            self.announce("thrift found, regenerating files in " + out)
            if not self.dry_run:
                self.spawn([thrift, '-out', out,
                            '-v', '--gen', 'py:twisted,new_style',
                            os.path.join(root, 'lacli', 'server', 'ClientInterface.thrift')])
        else:
            self.announce("thrift executable not found, skipping")

try:
    import pandoc
    pandoc.core.PANDOC_PATH = 'pandoc'
    readme = pandoc.Document()
    readme.markdown = open('README.md').read()
    description = readme.rst
except (IOError, ImportError):
    description = 'This is the prototype client program' + \
        'for interacting with the Longaccess service.'


class build_py(_build_py):
    def thrift_gen(self, files):
        pass

    def run(self):
        _build_py.run_command(self, 'gen_thrift')
        _build_py.run(self)

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
      cmdclass={'build_py': build_py, 'gen_thrift': gen_thrift},
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
