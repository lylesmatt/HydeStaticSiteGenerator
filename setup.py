from setuptools import setup, find_packages

setup(
    name='HydeStaticSiteGenerator',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    author='Matt Lyles',
    author_email='lyles.matt@gmail.com',
    description='A static site generator, inspired by Jekyll, but in Python and not so blog oriented.',
    install_requires=[
        'python-liquid',
        'Click'
    ],
    entry_points={
        'console_scripts': [
            'hyde = hyde.cli:cli',
        ],
    }
)
