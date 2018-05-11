from setuptools import setup


lines = []
with open('requirements.txt') as f:
    lines = [line.strip() for line in f.readlines()]

setup(
    name='keg-api',
    packages=['kegapi'],
    include_package_data=True,
    install_requires=lines,
)
