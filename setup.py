from setuptools import setup, find_packages

setup(version='0.1',
      name="lacli",
      author="Konstantinos Koukopoulos",
      description="The Long Access client",
      long_description=open('README').read(),
      packages=['lacli', 'lacli.t'],
      install_requires=['boto'],
      tests_require=['testtools'],
      test_suite="lacli.t",
      scripts=['bin/lacli.py']
)
