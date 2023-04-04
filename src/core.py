import os
from pathlib import Path
import subprocess
import yaml
import pty


class IndentedYamlDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentedYamlDumper, self).increase_indent(flow, False)
    

class Context:
    def __init__(self, root_dir: Path=None, is_initialized=False):
        if root_dir is None:
            raise ValueError("Critical error: context is missing project base directory.")
        self.root_dir = root_dir
        self.is_initialized = is_initialized
        self.activate_path = self.root_dir / "python_modules" / "bin" / "activate"

        self.lock_file_exists = os.path.exists(self.root_dir / "barn.lock")

        self.project_yaml_path = self.root_dir / "project.yaml"



    def __repr__(self) -> str:
        repr = f"""
        Root: {self.root_dir}
        Initialized: {self.is_initialized}
        Activate path: {self.activate_path}"
        """
        return repr

    def __run_command(self, command, mute=False):
        master_fd, slave_fd = pty.openpty()
        process = subprocess.Popen(
            command,
            executable="/bin/bash",
            shell=True,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True
        )

        os.close(slave_fd)
        stdout = []

        while True:
            try:
                data = os.read(master_fd, 1024).decode('utf-8')
                if not data:
                    break
                if not mute:
                    print(data, end='', flush=True)
                stdout.append(data)
            except OSError:
                break

        os.close(master_fd)
        process.wait()
        return ''.join(stdout), process.returncode
    
    def run_command_in_context(self, command: str):

        which_pip, exit_code = self.__run_command(
            f'source {self.activate_path} && which pip',
            mute=True
        )

        assert which_pip.strip() == f'{self.root_dir}/python_modules/bin/pip', "Fatal, Barn probably made a mistake, pip anti-global safeguard was not respected, aborting."


        stdout, exit_code = self.__run_command(
            f'source {self.activate_path} && {command}'
        )

        return stdout, exit_code
    
    def run_command_on_global(self, command: str):
        stdout, exit_code = self.__run_command(
            f'{command}'
        )
        return stdout, exit_code


    def get_project_config(self):
        # Load the YAML file
        with open(self.project_yaml_path, 'r') as yaml_file:
            yaml_content = yaml.safe_load(yaml_file)

        return yaml_content
    
    def add_dependency_to_project_yaml(self, package, version):
        yaml_content = self.get_project_config()
        new_entry = {
            package: {
                'version': version
            }
        }
        yaml_content["dependencies"].append(new_entry)
        with open(self.project_yaml_path, 'w') as yaml_file:
            yaml.dump(yaml_content, yaml_file, Dumper=IndentedYamlDumper, default_flow_style=False, indent=2, sort_keys=False)

    def remove_dependency_from_project_yaml(self, package):
        yaml_content = self.get_project_config()

        
        dependencies: list[any] = yaml_content["dependencies"]
        for index, dependency in enumerate(dependencies):
            if package in dependency:
                del dependencies[index]
                break
        
        yaml_content["dependencies"] = dependencies
        
            
        with open(self.project_yaml_path, 'w') as yaml_file:
            yaml.dump(yaml_content, yaml_file, Dumper=IndentedYamlDumper, default_flow_style=False, indent=2, sort_keys=False)

    def get_installed_version(self, package_name):
        return "LOOK_AT_LOCK"

        



def is_barn_project(base_dir: Path):
    return (
        (base_dir / "project.yaml").is_file()
    )

def is_env_initialized(base_dir: Path):
    return (
        (base_dir / "python_modules").is_dir() and
        (base_dir / "python_modules" / "bin" / "activate").is_file()
    )


def find_project_yaml():
    current_dir = Path.cwd()
    while current_dir != Path(current_dir.root):
        if is_barn_project(current_dir):
            return current_dir / "project.yaml"
        current_dir = current_dir.parent
    
    
    raise Exception("Barn could not find a project context to use. Are you in a project directory?")



def barn_action(action):
    project_yaml = find_project_yaml()
    root_dir = project_yaml.parent
    is_initialized = is_env_initialized(root_dir)
    context = Context(
        root_dir=root_dir,
        is_initialized=is_initialized
    )
    def wrapper(*args, **kwargs):
        action(*args, **kwargs, context=context)

    return wrapper
