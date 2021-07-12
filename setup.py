from __future__ import print_function

from juno_pipeline import juno_info
import sys

if sys.version_info < (3, 7): 
    print('At least Python 3.7 is required for the Juno pipelines to work.\n', 
            file=sys.stderr)
    exit(1)


try:
    from setuptools import setup, find_packages
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
    packages=find_packages(include=['juno_pipeline', 'juno_pipeline.*'], exclude='__main__'),
    scripts=['juno_pipeline/base_juno_pipeline.py'],
    package_data={'juno_pipeline': ['envs/*']},
    install_requires=[
        'dask',
        'mamba',
        'pip>=19.2.0',
        'snakemake>=6.1.0',
        'unittest2',
        'xlrd==1.2.0',
        'pyyaml>=5.4.1'
    ],
    entry_points={
        "console_scripts": [
            "juno_pipeline = juno_pipeline:main"
        ]
    },
    include_package_data=True
)