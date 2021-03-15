from setuptools import setup
from setuptools import find_packages

# list dependencies from file
with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(name='runinlyon',
      version="1.0",
      description="get running data",
      packages=find_packages(),
      install_requires=requirements,
      include_package_data=True,
      scripts=['scripts/runin-run']
     )

