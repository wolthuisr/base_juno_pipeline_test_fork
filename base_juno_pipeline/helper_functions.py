import subprocess
import pathlib

class TextHelpers:
    """Class with helper functions for text manipulation"""
    
    def color_text(self, text, color_code):
        """Function to convert normal text to color text """
        formatted_text = '\033[0;' + str(color_code) + 'm' + text + '\n\033[0;0m'
        return formatted_text

    def message_formatter(self, message):
        """Function to convert normal text to yellow text (for an 
        important message)"""
        return self.color_text(text=message, color_code=33)

    def error_formatter(self, message):
        """Function to convert normal text to red text (for an error)"""
        return self.color_text(text=message, color_code=31)


class FileHelpers:
    """Class with helper functions for file/dir validation and manipulation"""

    def validate_is_nonempty_file(self, file_path, min_file_size = 0):
        file_path = pathlib.Path(file_path)
        nonempty_file = (file_path.is_file() 
                            and file_path.stat().st_size >= min_file_size)
        if nonempty_file:
            return True
        else:
            return False


class GitHelpers:
    """Class with helper functions for handling git repositories"""
    
    def download_git_repo(self, version, url, dest_dir):
        """Function to download a git repo"""
        try:
            # If updating (or simply an unfinished installation is present)
            # the downloading will fail. Therefore, need to remove all 
            # directories with the same name
            rm_dir = subprocess.run(['rm','-rf', str(dest_dir)], 
                                    check = True, timeout = 60)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
            rm_dir.kill()
            raise

        dest_dir = pathlib.Path(dest_dir)
        dest_dir.parent.mkdir(exist_ok = True)
        
        try:
            downloading = subprocess.run(['git', 'clone', 
                                            '-b', version, 
                                            '--single-branch', '--depth=1', 
                                            url, str(dest_dir)],
                                            check = True,
                                            timeout = 500)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
            downloading.kill()
            raise
            
    def get_repo_url(self, gitrepo_dir):
        """Function to get the URL of a directory. It first checks wheter it
        is actually a repo (sometimes the code is just downloaded as zip and
        it is not considered a repo"""
        try:
            url = subprocess.check_output(["git","config", "--get", "remote.origin.url"],
                                            cwd = f'{str(gitrepo_dir)}').strip()
            url = url.decode()
        except:
            url = "Not available. This might be because this folder is not a repository or it was downloaded manually instead of through the command line."
        return url

    def get_commit_git(self, gitrepo_dir):
        """Function to get the commit number from a folder (must be a git repo)"""
        try:
            commit = subprocess.check_output(['git', 
                                            '--git-dir', 
                                            f'{str(gitrepo_dir)}/.git', 
                                            'log', '-n', '1', '--pretty=format:"%H"'],
                                            timeout = 30)
            commit = commit.decode()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            commit = "Not available. This might be because this folder is not a repository or it was downloaded manually instead of through the command line."                
        return commit


class JunoHelpers(TextHelpers, FileHelpers, GitHelpers):
    pass