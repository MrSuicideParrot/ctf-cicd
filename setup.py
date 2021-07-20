from setuptools import setup, find_packages

REQUIRES = [
    "ctfcli==0.0.8",
]

setup(
    name='ctfcicd',
    version='0.0.1',
    install_requires=REQUIRES,
    packages=find_packages(),
    url='https://github.com/MrSuicideParrot/ctf-cicd',
    license='MIT',
    author='André Cirne',
    description='Tool for CI/CD pipelines to deploy CTFs',
    entry_points={"console_scripts": ["ctfcicd = ctfcicd.__main__:main"]},
)
