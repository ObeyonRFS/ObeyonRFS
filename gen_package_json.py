import json
import os
import toml

os.chdir(os.path.dirname(os.path.abspath(__file__)))

json_file = open("package.json", "r")
package_json = json.load(json_file)
json_file.close()
package_json['urls'] = []
package_json['version'] = ""
with open(os.path.join(os.getcwd(), 'pyproject.toml'), 'r') as f:
    pyproject = toml.load(f)
    package_json['version'] = pyproject['tool']['poetry']['version']
    # for dep in pyproject['tool']['poetry']['dependencies']:
    #     package_json['deps'].append(dep)
    # for dep in pyproject['tool']['poetry']['dev-dependencies']:
    #     package_json['deps'].append(dep)
for root, dirs, files in os.walk("obeyon_rfs/"):
    if "__pycache__" in root:
        continue
    for file in files:
        path=os.path.join(root, file).replace("\\", "/")
        package_json['urls'].append(
            [path, "github:ObeyonRFS/ObeyonRFS/"+path]
        )

        # if file.endswith('.whl') or file.endswith('.tar.gz'):
        #     package_json['url'].append(os.path.join(root, file))

with open(os.path.join(os.getcwd(), 'package.json'), 'w') as f:
    json.dump(package_json, f, indent=2)