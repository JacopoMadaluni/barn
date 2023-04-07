from src.core import barn_action, Context


@barn_action
def add(requirement, context: Context=None):

    package_name, package_version = context.split_package_version(requirement)

    print(f"Name: {package_name}, version: {package_version}")

    requirement = f'{package_name}=={package_version}' if package_version is not None else package_name

    stdout, exit_code = context.run_command_in_context(f"pip install {requirement}")

    if exit_code == 0:
        context.run_command_in_context("pip freeze > barn.lock")
        installed_version = context.get_installed_version(package_name)
        context.add_dependency_to_project_yaml(package_name, installed_version)
    else:
        print(f"Error installing {package_name}=={package_version}")

