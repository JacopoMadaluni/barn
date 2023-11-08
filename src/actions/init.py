import os
import pkg_resources
import yaml

def init():
    def get_template_path(template_name):
        relative_path = os.path.join("templates", template_name)
        return pkg_resources.resource_filename("src", relative_path)
    

    print("Current working dir: ", os.getcwd())
    print(f"Template: {get_template_path('new-project/project.yml')}")

    project_info = {}

    project_info["name"] = input("Project name: ") or "my-project"
    project_info["version"] = input("Version (default: 0.1.0): ") or "0.1.0"
    project_info["description"] = input("Description: ") or ""
    project_info["author"] = input("Author: ") or ""
    project_info["license"] = input("License (default: MIT): ") or "MIT"

    # You can add more fields as needed

    print("\nProject information:")
    for key, value in project_info.items():
        print(f"{key}: {value}")

    with open(get_template_path('new-project/project.yml'), 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            data['name'] = project_info['name']
            data['version'] = project_info['version']
            data['description'] = project_info['description']
            data['author'] = project_info['author']
            data['license'] = project_info['license']

        except yaml.YAMLError as exc:
            print(exc)
            data = {}

    # Write the yaml back to the filesystem
    with open("./project.yaml", 'w+') as stream:
        try:
            yaml.dump(data, stream)
        except yaml.YAMLError as exc:
            print(exc)
