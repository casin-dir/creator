import sys
import getopt
import os
import shutil
import tempfile

from git import Repo

from generator import Generator
from utils.asker import ask


class Manager:
    def __init__(self):
        self.target_path = None
        self.target_name = None
        self.template_path = None
        self.generator = None
        self.is_remote_template = None

    def run(self):
        optlist, args = getopt.getopt(sys.argv[1:], 'p:t:h', ['path=', 'template=', 'help'])
        for opt, arg in optlist:
            if opt in ('-p', '--path'):
                self.target_path = arg
            elif opt in ('-t', '--template'):
                self.template_path = arg
            elif opt in ('-h', '--help'):
                self.print_help()
                return None
            else:
                sys.exit(1)

        if self.target_path is None:
            self.target_path = os.getcwd()

        self.try_get_template_path()
        while self.template_path is None:
            self.try_get_template_path()

        if len(args) == 0:
            while self.target_name is None:
                self.try_get_target_name()
        else:
            self.target_name = args[0]
        self.generate()

    def generate(self):
        temp_template_dir = None

        if self.is_remote_template:
            temp_template_dir = tempfile.mkdtemp()
            try:
                print('Cloning repo...')
                Repo.clone_from(self.template_path, temp_template_dir)
                shutil.rmtree(os.path.join(temp_template_dir, '.git'), ignore_errors=True)
            except OSError:
                shutil.rmtree(temp_template_dir, ignore_errors=True)
                print('*** Error, problem with git repo ***')
                print(OSError)
                sys.exit(2)
        else:
            temp_template_dir = self.template_path

        self.generator = Generator(temp_template_dir, self.target_path, self.target_name)
        self.generator.run()

        if self.is_remote_template:
            shutil.rmtree(temp_template_dir, ignore_errors=True)

    def try_get_template_path(self):

        if self.template_path is None:
            self.template_path = ask('Enter path to template (may git repo): ')

        if self.is_git_repo(self.template_path):
            self.is_remote_template = True

        if self.is_local_path(self.template_path):
            self.is_remote_template = False

        if self.is_remote_template is None:
            self.template_path = None
            print('Wrong path!')

    def try_get_target_name(self):
        self.target_name = ask('Enter project name (dir will be rewrite if exist): ')

        if len(self.target_name) < 1:
            self.target_name = None
            print('Wrong name!')

    @staticmethod
    def print_help():
        print('='*80)
        print('Welcome to Creator v 0.1.0\n')
        print('For *pro* run in any dir: \n    $ creator -t <path_to_template> '
              '-p <path_to_project_dir> <project_name>\n')
        print('For *newbies* run in dir where will be placed the project: \n    $ creator\n')
        print('<path_to_template> can be like: '
              '\n    \"https://github.com/casin-dir/test_template.git\"'
              '\n    \"~/Templates/my_template\"\n')
        print('<path_to_project_dir> can be like: '
              '\n    \"~/Projects\"')
        print('=' * 80)

    @staticmethod
    def is_git_repo(path):

        if len(path) < 5:
            return False

        return path[-4:] == '.git'

    @staticmethod
    def is_local_path(path):
        return os.path.exists(path)





