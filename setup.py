from setuptools import setup, find_packages

setup(version='0.1',
      packages=find_packages(),
      install_requires=['boto'],
      tests_require=['testtools'],
      test_suite="botofun.t",
)
