"""
The Juno pipeline library contains the basic classes to build a 
bacteriology genomics pipeline with the format used in the IDS-
bioinformatics group at the RIVM. All our pipelines use Snakemake.
"""

from datetime import datetime
import pathlib
import re
from snakemake import snakemake
import subprocess
from uuid import uuid4
import yaml

from base_juno_pipeline import helper_functions

class PipelineStartup(helper_functions.JunoHelpers):
    """Class with checkings for the input directory and to generate a 
    dictionary  with sample names and their corresponding input files 
    (sample_dict). Works for pipelines accepting fastq or fasta files 
    as input"""
    
    def __init__(self,
                input_dir, 
                input_type='fastq',
                min_file_size=0):

        self.input_dir = pathlib.Path(input_dir)
        self.input_type = input_type
        self.min_file_size = int(min_file_size)

        assert self.input_dir.is_dir(), \
            f"The provided input directory ({input_dir}) does not exist. Please provide an existing directory"
        assert self.input_type in ['fastq', 'fasta', 'both'], \
            "input_type to be checked can only be 'fastq', 'fasta' or 'both'"
        
        self.unique_id = uuid4()
        self.__subdirs_ = self.define_input_subdirs()
        self.validate_input_dir()
        print("Making a list of samples to be processed in this pipeline run...")
        self.sample_dict = self.make_sample_dict()
        print("Validating that all expected input files per sample are present in the input directory...")
        self.validate_sample_dict()

    def input_dir_is_juno_assembly_output(self):
        """Function to check whether the input directory is actually
        the output of the Juno_assembly pipeline. The Juno_assembly 
        pipeline is often the first step for downstream analyses."""
        is_juno_assembly_output = (self.input_dir.joinpath('clean_fastq').exists() 
                                        and self.input_dir.joinpath('de_novo_assembly_filtered').exists())
        if is_juno_assembly_output:
            return True
        else:
            return False

    def define_input_subdirs(self):
        """Function to check whether the input is from the Juno assembly 
        pipeline or just a simple input directory"""
        # Only when the input_dir comes from the Juno-assembly pipeline 
        # the fastq and fasta files do not need to be in the same 
        # folder (fastq are then expected in a subfolder called 
        # <input_dir>/clean_fastq and the fasta assembly files are
        # expected in a subfolder called <input_dir>/de_novo_assembly_filtered)
        if self.input_dir_is_juno_assembly_output():
            return {'fastq': self.input_dir.joinpath('clean_fastq'),
                    'fasta': self.input_dir.joinpath('de_novo_assembly_filtered')}
        else:
            return {'fastq': self.input_dir,
                    'fasta': self.input_dir}

    def validate_input_subdir(self, 
                                input_subdir, 
                                extension=('.fastq', '.fastq.gz', '.fq', '.fq.gz', '.fasta')):
        """Function to validate whether the subdirectories (if applicable)
        or the input directory have files that end with the expected extension"""
        for item in input_subdir.iterdir():
            if item.is_file():
                if str(item).endswith(extension):
                    return True
                    break 
        raise ValueError(self.error_formatter(
                                f'Input directory ({self.input_dir}) does not contain files that end with one of the expected extensions {extension}.'
                                            ))

    def validate_input_dir(self):
        """Function to check that input directory is indeed an existing 
        directory that contains files with the expected extension (fastq
        or fasta)"""
    
        if self.input_type == 'fastq':
            return self.validate_input_subdir(self.__subdirs_['fastq'], 
                                                ('.fastq', '.fastq.gz', '.fq', '.fq.gz'))
        elif self.input_type == 'fasta':
            return self.validate_input_subdir(self.__subdirs_['fasta'], 
                                                ('.fasta'))
        else:
            fastq_subdir_validated = self.validate_input_subdir(self.__subdirs_['fastq'], 
                                                                ('.fastq', '.fastq.gz', '.fq', '.fq.gz'))
            fasta_subdir_validated = self.validate_input_subdir(self.__subdirs_['fasta'], 
                                                                ('.fasta'))
            return (fastq_subdir_validated and fasta_subdir_validated)

    def enlist_fastq_samples(self):
        """Function to enlist the fastq files found in the input 
        directory. Returns a dictionary with the form 
        {sample: {R1: fastq_file1, R2: fastq_file2}}"""
        pattern = re.compile("(.*?)(?:_S\d+_|_S\d+.|_|\.)(?:p)?R?(1|2)(?:_.*\.|\..*\.|\.)f(ast)?q(\.gz)?")
        samples = {}
        for file_ in self.__subdirs_['fastq'].iterdir():
            if self.validate_is_nonempty_file(file_, self.min_file_size):
                match = pattern.fullmatch(file_.name)
                if match:
                    sample = samples.setdefault(match.group(1), {})
                    sample[f"R{match.group(2)}"] = str(file_)        
        return samples

    def enlist_fasta_samples(self):
        """Function to enlist the fasta files found in the input 
        directory. Returns a dictionary with the form 
        {sample: {assembly: fasta_file}}"""
        pattern = re.compile("(.*?).fasta")
        samples = {}
        for file_ in self.__subdirs_['fasta'].iterdir():
            if self.validate_is_nonempty_file(file_, self.min_file_size):
                match = pattern.fullmatch(file_.name)
                if match:
                    sample = samples.setdefault(match.group(1), {})
                    sample["assembly"] = str(file_)
        return samples            

    def make_sample_dict(self):
        """Function to make a sample sheet from the input directory (expecting 
        either fastq or fasta files as input)"""
        if self.input_type == 'fastq':
            samples = self.enlist_fastq_samples()
        elif self.input_type == 'fasta':
            samples = self.enlist_fasta_samples()
        else:
            samples = self.enlist_fastq_samples()
            samples_fasta = self.enlist_fasta_samples()
            for k in samples.keys():
                samples[k]['assembly'] = samples_fasta[k]['assembly']
        return samples

    def validate_sample_dict(self):
        if not self.sample_dict:
            raise ValueError(
                    self.error_formatter(f'The input directory ({self.input_dir}) does not contain any files with the expected format/naming.'))
        if self.input_type == 'fastq' or self.input_type == 'both':
            for sample in self.sample_dict:
                R1_present = 'R1' in self.sample_dict[sample].keys()
                R2_present = 'R2' in self.sample_dict[sample].keys()
                if (not R1_present or not R2_present):
                    raise KeyError(self.error_formatter(f'Either the R1 or R2 files are missing for sample {sample}. Paired-end reads are expected by the Juno pipelines. If you are sure you have paired-end reads, it might be that the names of some of your files are not being properly recognized'))
        if self.input_type == 'fasta' or self.input_type == 'both':
            for sample in self.sample_dict:
                assembly_present = self.sample_dict[sample].keys()
                if 'assembly' not in assembly_present:
                    raise KeyError(self.error_formatter(f'The assembly is mising for sample {sample}. This pipeline expects an assembly per sample.'))



class RunSnakemake(helper_functions.JunoHelpers):
    """Class with necessary input to run Snakemake"""

    def __init__(self,
                pipeline_name,
                pipeline_version,
                output_dir,
                workdir,
                sample_sheet=pathlib.Path('config/sample_sheet.yaml'), 
                user_parameters=pathlib.Path('config/user_parameters.yaml'), 
                fixed_parameters=pathlib.Path('config/pipeline_parameters.yaml'),
                snakefile='Snakefile',
                cores=300,
                local=False,
                queue='bio',
                unlock=False,
                rerunincomplete=True,
                dryrun=False,
                useconda=True,
                conda_frontend='mamba',
                usesingularity=True,
                singularityargs='',
                restarttimes=0,
                latency_wait=60):
        self.pipeline_name=pipeline_name
        self.pipeline_version=pipeline_version
        self.date_and_time=datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        self.hostname=str(subprocess.check_output(['hostname']).strip())
        self.output_dir=pathlib.Path(output_dir)
        self.workdir=pathlib.Path(workdir)
        self.sample_sheet=sample_sheet
        self.user_parameters=user_parameters
        self.fixed_parameters=fixed_parameters
        self.snakefile=snakefile
        self.path_to_audit=self.output_dir.joinpath('audit_trail')
        self.cores=cores
        self.local=local
        self.queue=queue
        self.unlock=unlock
        self.dryrun=dryrun
        self.rerunincomplete=rerunincomplete
        self.useconda=useconda
        self.conda_frontend='mamba'
        self.usesingularity=usesingularity
        self.singularityargs=singularityargs
        self.restarttimes=restarttimes
        self.latency=latency_wait
        # Generate pipeline audit trail
        self.path_to_audit.mkdir(parents=True, exist_ok=True)
        self.audit_trail = self.generate_audit_trail()


    def get_git_audit(self, git_file):
        """Function to get URL and commit from pipeline repo 
        (if downloaded through git)"""
        print(self.message_formatter(f"Collecting information about the Git repository of this pipeline (see {git_file})"))
        git_audit = {"repo": self.get_repo_url('.'),
                    "commit": self.get_commit_git('.')}
        with open(git_file, 'w') as file:
            yaml.dump(git_audit, file, default_flow_style=False)

    def get_pipeline_audit(self, pipeline_file):
        print(self.message_formatter("Collecting information about the pipeline (see {pipeline_file})"))
        pipeline_info = {'pipeline_name': self.pipeline_name,
                        'pipeline_version': self.pipeline_version,
                        'timestamp': self.date_and_time,
                        'hostname': self.hostname}
        with open(pipeline_file, 'w') as file:
            yaml.dump(pipeline_info, file, default_flow_style=False)

    def get_conda_audit(self, conda_file):
        print(self.message_formatter("Getting information of the master environment used for this pipeline."))
        conda_audit = subprocess.check_output(["conda","list"]).strip()
        with open(conda_file, 'w') as file:
            file.writelines("Master environment list:\n\n")
            file.write(str(conda_audit))

    def generate_audit_trail(self):
        assert pathlib.Path(self.sample_sheet).exists(), \
            f"The sample sheet ({str(sample_sheet)}) does not exist. This sample sheet is generated before starting your pipeline. Something must have gone wrong while creating it."
        assert pathlib.Path(self.user_parameters).exists(), \
            f"The provided user_parameters ({','.join(self.user_parameters)}) was not created properly or was deleted before starting the pipeline"

        git_file = self.path_to_audit.joinpath('log_git.yaml')
        self.get_git_audit(git_file)
        conda_file = self.path_to_audit.joinpath('log_conda.txt')
        self.get_conda_audit(conda_file)
        pipeline_file = self.path_to_audit.joinpath('log_pipeline.yaml')
        self.get_pipeline_audit(pipeline_file)
        user_parameters_file = self.path_to_audit.joinpath('user_parameters.yaml')
        samples_file = self.path_to_audit.joinpath('sample_sheet.yaml')
        audit_sample_sheet = subprocess.Popen(['cp', self.sample_sheet, samples_file])
        audit_userparams = subprocess.Popen(['cp', self.user_parameters, user_parameters_file])
        return [git_file, conda_file, pipeline_file, user_parameters_file, samples_file]

    def run_snakemake(self):

        print(self.message_formatter(f"Running {self.pipeline_name} pipeline."))

        if self.local:
            print(self.message_formatter("Jobs will run locally"))
            cluster = None
        else:
            print(self.message_formatter("Jobs will be sent to the cluster"))
            cluster_log_dir = pathlib.Path(str(self.output_dir)).joinpath('log', 'cluster')
            cluster_log_dir.mkdir(parents=True, exist_ok=True)
            cluster = "bsub -q %s \
                    -n {threads} \
                    -o %s/{name}_{wildcards}_{jobid}.out \
                    -e %s/{name}_{wildcards}_{jobid}.err \
                    -R \"span[hosts=1]\" \
                    -M {resources.mem_gb}G \
                    -W 60" % (str(self.queue), str(cluster_log_dir), str(cluster_log_dir))
        
        pipeline_run_successful = snakemake(self.snakefile,
                                    workdir=self.workdir,
                                    configfiles=[self.user_parameters, self.fixed_parameters],
                                    config={"sample_sheet": str(self.sample_sheet)},
                                    cores=self.cores,
                                    nodes=self.cores,
                                    cluster=cluster,
                                    jobname=self.pipeline_name + "_{name}.jobid{jobid}",
                                    use_conda=self.useconda,
                                    conda_frontend=self.conda_frontend,
                                    use_singularity=self.usesingularity,
                                    singularity_args=self.singularityargs,
                                    keepgoing=True,
                                    printshellcmds=True,
                                    force_incomplete=self.rerunincomplete,
                                    restart_times=self.restarttimes, 
                                    latency_wait=self.latency,
                                    unlock=self.unlock,
                                    dryrun=self.dryrun)
        assert pipeline_run_successful, self.error_formatter(f"An error occured while running the {self.pipeline_name} pipeline.")
        print(self.message_formatter(f"Finished running {self.pipeline_name} pipeline!"))
        return pipeline_run_successful

        