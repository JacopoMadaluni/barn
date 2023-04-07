import subprocess
from src.core import barn_action, Context

@barn_action
def install(context: Context=None):
    if not context.is_initialized:
        print("Initializing python_modules")
        context.run_command_on_global("python -m venv python_modules")

    if not context.lock_file_exists:
        context.install_from_project()
    else:
        print("Installing..")
        # context.run_command_in_context("pip install -r barn.lock")
        context.install_from_project()
