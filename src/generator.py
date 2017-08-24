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
        children_names_without_chunks = []

        chunks = []

        for child_name in children_names:
            if self.is_chunk(child_name):
                chunk_pure_name = self.get_chunk_pure_name(child_name)
                chunks.append({
                    'pure_name': chunk_pure_name,
                    'path': os.path.join(dir_path, child_name),
                })
            else:
                children_names_without_chunks.append(child_name)

        for child_name in children_names_without_chunks:
            child_path = os.path.join(dir_path, child_name)

            if os.path.isdir(child_path):
                self.handle_template_dir(child_path, target_dir_path)

            if os.path.isfile(child_path):
                self.handle_dir_file(child_path, target_dir_path, chunks)

    def handle_dir_file(self, file_path, target_path, chunks):

        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        need_build, pure_name = self.ask_params_and_get_pure_name(file_name)
        if need_build is False:
            return None

        try:
            with open(file_path, 'r',  encoding='utf8') as template_file:
                with open(os.path.join(target_path, pure_name), 'w', encoding='utf8') as target_file:
                    for line in template_file:
                        if self.is_chunk(line):
                            for chunk_info in chunks:
                                chunk_pure_name = chunk_info['pure_name']
                                chunk_path = chunk_info['path']
                                if chunk_pure_name in line:
                                    if self.need(chunk_pure_name):
                                        with open(chunk_path, 'r', encoding='utf8') as chunk_file:
                                            line = chunk_file.read() + '\n'
                                    else:
                                        line = ''
                                        break
                        target_file.write(line)
        except:
            print('*** File ' + file_name + ' in ' + file_dir + ' has been ignored ***')
            return None

    def ask_params_and_get_pure_name(self, name):
        if '?' in name:
            name_chunks = name.split('?')
            params_names = name_chunks[:-1]
            pure_name = name_chunks[-1]

            for param_name in params_names:
                param_value = self.need(param_name)
                if param_value is False:
                    return False, pure_name

            return True, pure_name
        else:
            return True, name

    def need(self, param_name):
        param_value = self.params.get(param_name)
        if param_value is None:
            param_value = ask(
                'Need ' + param_name + '? (y/n): ',
                lambda res: res in ('y', 'n'),
                lambda res: res == 'y'
            )

        self.params[param_name] = param_value
        return param_value

    @staticmethod
    def make_dir(path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    @staticmethod
    def is_chunk(str_to_check):
        if '@' in str_to_check:
            return True

        return False

    @staticmethod
    def get_chunk_pure_name(name):
        return os.path.splitext(name.split('@')[1])[0]
