from __future__ import print_function

from juno_pipeline import juno_info
import sys

if sys.version_info < (3, 7): 
    print('At least Python 3.7 is required for the Juno pipelines to work.\n', 
            file=sys.stderr)
    exit(1)


try:
    from setuptools import setup
except ImportError:
    print('Please install setuptools before installing the Juno_pipeline library.\n', 
    file=sys.stderr)
    exit(1)


setup(
    name=juno_info.__package_name__,
    version=juno_info.__version__,
    author=juno_info.__authors__,
    author_email=juno_info.__email__,
    description=juno_info.__description__,
    zip_safe=False,
    license=juno_info.__license__,
    packages='juno_pipeline',
    scripts=[
        'juno_pipeline/juno_pipeline.py'],
    package_data={'juno_pipeline': ['envs/*']},
    install_requires=[
        'dask',
        'git',
        'mamba',
        'pip>=19.2.0',
        'snakemake>=6.1.0',
        'unittest',
        'xlrd==1.2.0',
        'yaml>=5.4.1'
    ],
    entry_points={
        "console_scripts": [
            "juno_pipeline = juno_pipeline:main"
        ]
    },
    keywords=[],
    include_package_data=True
)