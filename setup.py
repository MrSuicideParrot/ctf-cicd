from setuptools import setup, find_packages

REQUIRES = [
    "docker~=5.0.2",
    "requests~=2.22.0",
    "PyYAML~=5.4",
    "paramiko",
    "docker-compose"
]

setup(
    name='ctfcicd',
    version='0.1.10',
    install_requires=REQUIRES,
    packages=find_packages(),
    url='https://github.com/MrSuicideParrot/ctf-cicd',
    license='MIT',
    author='André Cirne',
    description='Tool for CI/CD pipelines to deploy CTFs',
    entry_points={"console_scripts": ["ctfcicd = ctfcicd.__main__:main"]},
)
