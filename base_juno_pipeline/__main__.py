import argparse
import pathlib
import sys

import juno_info
import base_juno_pipeline


def get_args():
    parser=argparse.ArgumentParser(
        description='Juno pipeline. Automated pipeline for bacterial genomics.'
    )
    parser.add_argument(
        '-i',
        '--input',
        type=pathlib.Path,
        required=True,
        metavar='DIR',
        help='Relative or absolute path to the input directory. It must contain the expected input files or be the output directory of the Juno-assembly pipeline.'
    )
    parser.add_argument(
        '--type',
        default='both',
        choices=['fastq', 'fasta', 'both'],
        help='Expected input type of files in input directory.'
    )
    parser.add_argument(
        '-m',
        '--minfilesize',
        type=int,
        default=0,
        metavar='INT',
        help='Minimum file size (in bytes) of input files. Files smaller than that will not be run through the pipeline.'
    )
    parser.add_argument(
        '--pipelinename',
        type=str,
        metavar='STR',
        default='Juno',
        help='Pipeline name.'
    )
    parser.add_argument(
        '-v',
        '--v',
        type=str,
        metavar='VERSION',
        default='NA',
        help='Pipeline version.'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=pathlib.Path,
        metavar='DIR',
        default='output',
        help='Relative or absolute path to the output directory. ' 
        'If non is given, an "output" directory will be created in '
        'the current directory.'
    )
    parser.add_argument(
        '-wd',
        '--workingdir',
        type=pathlib.Path,
        metavar='DIR',
        default='.',
        help='Relative or absolute path to the working directory of the '
        'pipeline. If non is given the current directory is used.'
    )
    parser.add_argument(
        '-s',
        '--samplesheet',
        type=pathlib.Path,
        metavar='FILE',
        default='config/sample_sheet.yaml',
        help='Path to sample sheet file to be created'
    )
    parser.add_argument(
        '-pp',
        '--pipelineparameters',
        type=pathlib.Path,
        metavar='FILE',
        default='config/pipeline_parameters.yaml',
        help='Path to pipeline parameters file to be created'
    )
    parser.add_argument(
        '-up',
        '--userparameters',
        type=pathlib.Path,
        metavar='FILE',
        default='config/user_parameters.yaml',
        help='Path to user parameters file to be created'
    )
    parser.add_argument(
        '-f',
        '--snakefile',
        type=pathlib.Path,
        metavar='FILE',
        default='Snakefile',
        help='Path to sample sheet file to be created'
    )
    parser.add_argument(
        '--useconda',
        action='store_true',
        help='Use conda environments in the pipeline.'
    )
    parser.add_argument(
        '--conda_frontend',
        default='mamba',
        choices=['conda', 'mamba'],
        help='Frontend to use for building conda environments (conda or mamba)'
    )
    parser.add_argument(
        '--usesingularity',
        action='store_true',
        help='Use singularity containers in the pipeline.'
    )
    parser.add_argument(
        '--singularityargs',
        type=str,
        metavar='STR',
        default='',
        help='Arguments to be passed to singularity'
    )
    parser.add_argument(
        '--restarttimes',
        type=int,
        default=0,
        metavar='INT',
        help='Number of times to restart each step of the pipeline if it fails.'
    )
    parser.add_argument(
        '--latencywait',
        type=int,
        default=60,
        metavar='INT',
        help='how many seconds to wait for an output file to appear after the execution of a job, e.g. to handle filesystem latency.'
    )
    parser.add_argument(
        '-q',
        '--queue',
        type=str,
        metavar='STR',
        default='bio',
        help='Name of the queue that the job will be submitted to if working'
        'on a cluster.'
    )
    parser.add_argument(
        '-l',
        '--local',
        action='store_true',
        help='Running pipeline locally (instead of in a computer cluster). Default is running it in a cluster.'
    )
    parser.add_argument(
        '-u',
        '--unlock',
        action='store_true',
        help='Unlock output directory (passed to snakemake).'
    )
    parser.add_argument(
        '-n',
        '--dryrun',
        action='store_true',
        help='Dry run printing steps to be taken in the pipeline without actually running it (passed to snakemake).'
    )
    parser.add_argument(
        '--rerunincomplete',
        action='store_true',
        help='Re-run jobs if they are marked as incomplete (passed to snakemake).'
    )
    args=parser.parse_args()
    return args


def main():
    """Main entry point."""
    print(f'{juno_info.__package_name__}')
    print(f'{juno_info.__description__}')
    print(f'Version: {juno_info.__version__}')
    print(f'License: {juno_info.__license__}')
    print(f'Author: {juno_info.__authors__}')
    print(f'Contact email: {juno_info.__email__}')
    args=get_args()
    print(args)


if __name__ == '__main__':
    sys.exit(main())