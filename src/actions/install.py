import subprocess
from src.core import barn_action, Context

@barn_action
def install(context: Context=None):
    if not context.is_initialized:
        print("Initializing python_modules")
        context.run_command_on_global("python -m venv python_modules")

    if not context.lock_file_exists:
        print("Lock file does not exist.")
        print("Handling project.yaml still not supported. Soon though")
    else:
        print("Installing..")
        context.run_command_in_context("pip install -r barn.lock")
