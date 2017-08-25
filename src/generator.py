import os
import shutil
import subprocess

import config
from utils.asker import ask


class Generator:
    def __init__(self, template_path, target_path, target_name):
        self.target_path = os.path.abspath(target_path)
        self.target_name = target_name
        self.template_root = os.path.abspath(template_path)

        self.params = {}

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

        user_script_path = None

        filtered_children_names = []

        chunks = []

        files_to_ignore = config.DEFAULT_IGNORED_FILES

        if config.CREATOR_IGNORE_FILE in children_names:
            with open(os.path.join(dir_path, config.CREATOR_IGNORE_FILE), 'r',  encoding='utf8') as ignore_file:
                for line in ignore_file:
                    file_name_to_ignore = line.rstrip()
                    if len(file_name_to_ignore) > 0:
                        files_to_ignore.append(file_name_to_ignore)

        if config.CREATOR_SCRIPT_FILE in children_names:
            user_script_path = os.path.join(dir_path, config.CREATOR_SCRIPT_FILE)
            self.run_user_script(
                user_script_path,
                config.CREATOR_SCRIPT_STAGE_BEFORE,
            )

        for child_name in children_names:
            if self.is_chunk(child_name):
                chunk_pure_name = self.get_chunk_pure_name(child_name)
                chunks.append({
                    'pure_name': chunk_pure_name,
                    'path': os.path.join(dir_path, child_name),
                })
            elif child_name not in files_to_ignore:
                filtered_children_names.append(child_name)

        for child_name in filtered_children_names:
            child_path = os.path.join(dir_path, child_name)

            if os.path.isdir(child_path):
                self.handle_template_dir(child_path, target_dir_path)

            if os.path.isfile(child_path):
                self.handle_dir_file(child_path, target_dir_path, chunks, user_script_path)

        if user_script_path is not None:
            self.run_user_script(
                user_script_path,
                config.CREATOR_SCRIPT_STAGE_AFTER,
            )

    def handle_dir_file(self, file_path, target_path, chunks, user_script_path):

        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        need_build, pure_name = self.ask_params_and_get_pure_name(file_name)
        if need_build is False:
            return None

        if user_script_path is not None:
            self.run_user_script(
                user_script_path,
                config.CREATOR_SCRIPT_STAGE_BEFORE,
                pure_name
            )

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

        if user_script_path is not None:
            self.run_user_script(
                user_script_path,
                config.CREATOR_SCRIPT_STAGE_AFTER,
                pure_name
            )

    def ask_params_and_get_pure_name(self, name):
        if config.LOGIC_PARAM_SYMBOL in name:
            name_chunks = name.split(config.LOGIC_PARAM_SYMBOL)
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
    def run_user_script(script_path, stage, item=config.CREATOR_SCRIPT_ITEM_ROOT):
        subprocess.call('chmod +x ' + script_path, shell=True)
        subprocess.call(
            config.CREATOR_SCRIPT_STAGE_VARIABLE + '={0} ' +
            config.CREATOR_SCRIPT_ITEM_VARIABLE + '={1} '
            '{2}'.format(stage, item, script_path),
            shell=True
        )

    @staticmethod
    def make_dir(path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    @staticmethod
    def is_chunk(str_to_check):
        if config.CHUNK_SYMBOL in str_to_check:
            return True

        return False

    @staticmethod
    def get_chunk_pure_name(name):
        return os.path.splitext(name.split(config.CHUNK_SYMBOL)[1])[0]
