import os
import shutil

from utils.asker import ask


class Generator:
    def __init__(self, template_path, target_path, target_name):
        self.target_path = os.path.abspath(target_path)
        self.target_name = target_name
        self.template_root = os.path.abspath(template_path)

        self.params = {}
        self.dirs_templates = {}

    def run(self):
        self.handle_template_dir(self.template_root, self.target_path, self.target_name)

    def handle_template_dir(self, dir_path, target_path, target_name=None):
        dir_name = os.path.basename(dir_path)
        need_make, pure_name = self.ask_params_and_get_pure_name(dir_name)

        if need_make is False:
            return None

        if target_name is not None:
            pure_name = target_name

        target_dir_path = os.path.join(target_path, pure_name)
        self.make_dir(target_dir_path)

        children_names = os.listdir(dir_path)

        for child_name in children_names:
            child_path = os.path.join(dir_path, child_name)

            if os.path.isdir(child_path):
                self.handle_template_dir(child_path, target_dir_path)

            if os.path.isfile(child_path):
                self.handle_dir_file(child_path, target_dir_path)

        print(self.dirs_templates)
        print('build templates here')

    def handle_dir_file(self, file_path, target_path):

        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        dir_templates = self.dirs_templates.get(file_dir)
        if dir_templates is None:
            self.dirs_templates[file_dir] = {}

        is_chunk, chunk_name, template_name = self.is_chunk_file(file_name)

        if is_chunk is True:
            template_info = self.dirs_templates[file_dir].get(template_name)

            if template_info is None:
                self.dirs_templates[file_dir][template_name] = {
                    'need_build': True,
                    'file_path': None,
                    'chunks': [],
                }

            template_info = self.dirs_templates[file_dir][template_name]

            template_info['chunks'].append({
                'chunk_name': chunk_name,
                'chunk_path': file_path,
            })

            return None

        need_build, pure_name = self.ask_params_and_get_pure_name(file_name)
        template_info = self.dirs_templates[file_dir].get(pure_name)

        if template_info is None:
            self.dirs_templates[file_dir][pure_name] = {
                'need_build': True,
                'file_path': None,
                'chunks': [],
            }

        self.dirs_templates[file_dir][pure_name]['need_build'] = need_build
        self.dirs_templates[file_dir][pure_name]['file_path'] = file_path
        print('prec')

    def ask_params_and_get_pure_name(self, name):
        if '?' in name:
            name_chunks = name.split('?')
            params_names = name_chunks[:-1]
            pure_name = name_chunks[-1]

            for param_name in params_names:
                param_value = self.params.get(param_name)
                if param_value is None:
                    param_value = self.need(param_name)

                self.params[param_name] = param_value
                if param_value is False:
                    return False, pure_name

            return True, pure_name
        else:
            return True, name

    @staticmethod
    def need(param_name):
        return ask(
            'Need ' + param_name + '? (y/n): ',
            lambda res: res in ('y', 'n'),
            lambda res: res == 'y'
        )

    @staticmethod
    def make_dir(path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    @staticmethod
    def is_chunk_file(name):
        if '@' in name:
            name_params = name.split('@')
            chunk_name = name_params[:-1][0]
            template_name = name_params[-1]
            return True, chunk_name, template_name
        else:
            return False, None, None
