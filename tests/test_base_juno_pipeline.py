import os
import pathlib
from sys import path
import unittest

main_script_path = str(pathlib.Path(pathlib.Path(__file__).parent.absolute()).parent.absolute())
path.insert(0, main_script_path)
from base_juno_pipeline import base_juno_pipeline
from base_juno_pipeline import helper_functions


class TestJunoHelpers(unittest.TestCase):
    """Testing Helper Functions"""

    def test_git_url_of_base_juno_pipeline(self):
        """Testing if the git URL is retrieved properly (taking this folder
        as example"""
        url = helper_functions.GitHelpers.get_repo_url(self, '.')
        url_equal_package_url = url == b'https://github.com/RIVM-bioinformatics/base_juno_pipeline.git'
        url_not_available = url == 'Not available. This might be because this folder is not a repository or it was downloaded manually instead of through the command line.'
        correct_url_result = url_equal_package_url or url_not_available
        self.assertTrue(correct_url_result)

    def test_fail_when_dir_not_repo(self):
        """Testing that the url is 'not available' when the directory is not
        a git repo"""
        self.assertEqual(helper_functions.GitHelpers.get_repo_url(self, 
                                                                    os.path.expanduser('~')),
                        'Not available. This might be because this folder is not a repository or it was downloaded manually instead of through the command line.')
    
    def test_get_commit_git(self):
        """Testing that the git commit function works"""
        self.assertIsInstance(helper_functions.GitHelpers.get_commit_git(self,
                                                                        '.'), bytes)

    def test_get_commit_git(self):
        """Testing that the git commit function gives right output when no git repo"""
        self.assertIsInstance(helper_functions.GitHelpers.get_commit_git(self,
                                                                        os.path.expanduser('~')), str)
        self.assertEqual(helper_functions.GitHelpers.get_commit_git(self,
                                                                    os.path.expanduser('~')), 
                        'Not available. This might be because this folder is not a repository or it was downloaded manually instead of through the command line.')


class TestPipelineStartup(unittest.TestCase):
    """Testing the pipeline startup (generating dict with samples) from general
    Juno pipelines"""
    
    def setUpClass(): 
        """Making fake directories and files to test different case scenarios 
        for starting pipeline"""

        fake_dirs = ['fake_dir_empty', 
                    'fake_dir_wsamples', 
                    'fake_dir_incomplete',
                    'fake_dir_juno', 
                    'fake_dir_juno/clean_fastq', 
                    'fake_dir_juno/de_novo_assembly_filtered',
                    'fake_wrong_fastq_names']

        fake_files = ['fake_dir_wsamples/sample1_R1.fastq',
                    'fake_dir_wsamples/sample1_R2.fastq.gz',
                    'fake_dir_wsamples/sample2_R1_filt.fq',
                    'fake_dir_wsamples/sample2_R2_filt.fq.gz', 
                    'fake_dir_wsamples/sample1.fasta',
                    'fake_dir_wsamples/sample2.fasta',
                    'fake_dir_incomplete/sample1_R1.fastq',
                    'fake_dir_incomplete/sample1_R2.fastq.gz',
                    'fake_dir_incomplete/sample2_R1_filt.fq',
                    'fake_dir_incomplete/sample2_R2_filt.fq.gz',
                    'fake_dir_incomplete/sample2.fasta',
                    'fake_dir_juno/clean_fastq/1234_R1.fastq.gz',
                    'fake_dir_juno/clean_fastq/1234_R2.fastq.gz', 
                    'fake_dir_juno/de_novo_assembly_filtered/1234.fasta',
                    'fake_wrong_fastq_names/1234_1_R1.fastq.gz',
                    'fake_wrong_fastq_names/1234_1_R2.fastq.gz']     
                    
        for folder in fake_dirs:
            pathlib.Path(folder).mkdir(exist_ok = True)
        for file_ in fake_files:
            pathlib.Path(file_).touch(exist_ok = True)

    def tearDownClass():
        """Removing fake directories/files"""

        fake_dirs = ['fake_dir_empty', 
                    'fake_dir_wsamples', 
                    'fake_dir_incomplete',
                    'fake_dir_juno', 
                    'fake_dir_juno/clean_fastq', 
                    'fake_dir_juno/de_novo_assembly_filtered',
                    'fake_wrong_fastq_names']

        for folder in fake_dirs:
            os.system('rm -rf {}'.format(str(folder)))

    def test_nonexisting_dir(self):
        """Testing the pipeline startup fails if the input directory does not 
        exist"""
        self.assertRaises(AssertionError, 
                            base_juno_pipeline.PipelineStartup, 
                            pathlib.Path('unexisting'), 
                            'both')

    def test_emptydir(self):
        """Testing the pipeline startup fails if the input directory does not 
        have expected files"""
        self.assertRaises(ValueError, 
                            base_juno_pipeline.PipelineStartup, 
                            pathlib.Path('fake_dir_empty'), 
                            'both')

    def test_incompletedir(self):
        """Testing the pipeline startup fails if the input directory is 
        missing some of the fasta files for the fastq files"""
        self.assertRaises(KeyError, 
                            base_juno_pipeline.PipelineStartup, 
                            pathlib.Path('fake_dir_incomplete'), 'both')

    def test_correctdir_fastq(self):
        """Testing the pipeline startup accepts fastq and fastq.gz files"""

        expected_output = {'sample1': {'R1': str(pathlib.Path('fake_dir_wsamples').joinpath('sample1_R1.fastq')), 
                                        'R2': str(pathlib.Path('fake_dir_wsamples').joinpath('sample1_R2.fastq.gz'))}, 
                            'sample2': {'R1': str(pathlib.Path('fake_dir_wsamples').joinpath('sample2_R1_filt.fq')), 
                                        'R2': str(pathlib.Path('fake_dir_wsamples').joinpath('sample2_R2_filt.fq.gz'))}}
        pipeline = base_juno_pipeline.PipelineStartup(pathlib.Path('fake_dir_wsamples'), 'fastq')
        self.assertDictEqual(pipeline.sample_dict, expected_output)
        
    def test_correctdir_fasta(self):
        """Testing the pipeline startup accepts fasta"""

        expected_output = {'sample1': {'assembly': str(pathlib.Path('fake_dir_wsamples').joinpath('sample1.fasta'))}, 
                            'sample2': {'assembly': str(pathlib.Path('fake_dir_wsamples').joinpath('sample2.fasta'))}}
        pipeline = base_juno_pipeline.PipelineStartup(pathlib.Path('fake_dir_wsamples'), 'fasta')
        self.assertDictEqual(pipeline.sample_dict, expected_output)
        
    def test_correctdir_both(self):
        """Testing the pipeline startup accepts both types"""

        expected_output = {'sample1': {'R1': str(pathlib.Path('fake_dir_wsamples').joinpath('sample1_R1.fastq')), 
                                        'R2': str(pathlib.Path('fake_dir_wsamples').joinpath('sample1_R2.fastq.gz')), 
                                        'assembly': str(pathlib.Path('fake_dir_wsamples').joinpath('sample1.fasta'))}, 
                            'sample2': {'R1': str(pathlib.Path('fake_dir_wsamples').joinpath('sample2_R1_filt.fq')), 
                                        'R2': str(pathlib.Path('fake_dir_wsamples').joinpath('sample2_R2_filt.fq.gz')), 
                                        'assembly': str(pathlib.Path('fake_dir_wsamples').joinpath('sample2.fasta'))}}
        pipeline = base_juno_pipeline.PipelineStartup(pathlib.Path('fake_dir_wsamples'), 'both')
        self.assertDictEqual(pipeline.sample_dict, expected_output)

    def test_files_smaller_than_minlen(self):
        """Testing the pipeline startup fails if you set a min_file_size 
        different than 0"""

        self.assertRaises(ValueError, 
                            base_juno_pipeline.PipelineStartup, 
                            pathlib.Path('fake_dir_incomplete'), 
                            'both',
                            min_file_size = 1000)

    def test_junodir_wnumericsamplenames(self):
        """Testing the pipeline startup converts numeric file names to 
        string"""

        expected_output = {'1234': {'R1': str(pathlib.Path('fake_dir_juno').joinpath('clean_fastq', '1234_R1.fastq.gz')), 
                                        'R2': str(pathlib.Path('fake_dir_juno').joinpath('clean_fastq', '1234_R2.fastq.gz')), 
                                        'assembly': str(pathlib.Path('fake_dir_juno').joinpath('de_novo_assembly_filtered', '1234.fasta'))}}
                
        pipeline = base_juno_pipeline.PipelineStartup(pathlib.Path('fake_dir_juno'), 'both')
        self.assertDictEqual(pipeline.sample_dict, expected_output)

    def test_string_accepted_as_inputdir(self):
        """Testing the pipeline startup accepts string (not only pathlib.Path)
        as input"""

        expected_output = {'1234': {'R1': str(pathlib.Path('fake_dir_juno').joinpath('clean_fastq', '1234_R1.fastq.gz')), 
                                        'R2': str(pathlib.Path('fake_dir_juno').joinpath('clean_fastq/1234_R2.fastq.gz')), 
                                        'assembly': str(pathlib.Path('fake_dir_juno').joinpath('de_novo_assembly_filtered','1234.fasta'))}}
                
        pipeline = base_juno_pipeline.PipelineStartup('fake_dir_juno', 'both')
        self.assertDictEqual(pipeline.sample_dict, expected_output)

    def test_fail_with_wrong_fastq_naming(self):
        """Testing the pipeline startup fails with wrong fastq naming (name 
        contains _1_ in the sample name)"""
        self.assertRaises(KeyError, 
                            base_juno_pipeline.PipelineStartup, 
                            pathlib.Path('fake_wrong_fastq_names'), 
                            'fastq')


if __name__ == '__main__':
	unittest.main()