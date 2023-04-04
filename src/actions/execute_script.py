import subprocess
from src.core import barn_action, Context
@barn_action
def execute_script(script_name, context: Context=None):
    config = context.get_project_config()
    scripts = config['scripts']
    script_to_execute = None
    for script in scripts:
        if script_name in script:
            script_to_execute = script[script_name]
    return context.run_command_in_context(script_to_execute)
