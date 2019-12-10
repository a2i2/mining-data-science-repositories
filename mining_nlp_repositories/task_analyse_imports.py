import os
import subprocess
import collections
from surround import Config

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']


def analyse_imports(repo_dir, output_dir):
    # mapping of import_name -> count
    imports = collections.defaultdict(int)

    for dirname in os.listdir(path=repo_dir):
        repo = os.path.join(repo_dir, dirname)
        result = subprocess.run(["findimports", repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if len(result.stderr) > 0:
            with open(os.path.join(output_dir, 'imports-' + dirname + '.err'), 'wb') as f:
                f.write(result.stderr)

        if len(result.stdout) > 0:
            with open(os.path.join(output_dir, 'imports-' + dirname + '.out'), 'wb') as f:
                f.write(result.stdout)

        # strip out duplicate imports
        module_imports = set()

        result_str = result.stdout.decode('utf-8')
        for line in result_str.split('\n'):
            import_str = line.strip()
            if import_str == "":
                # ignore blank lines
                continue
            if import_str.endswith(":"):
                # ignore module names (only interested in imports)
                continue
            else:
                module_imports.add(import_str.split(".")[0])

        if len(module_imports) > 0:
            with open(os.path.join(output_dir, 'imports-' + dirname + '.modules'), 'w') as f:
                for i in module_imports:
                    f.write(str(i) + '\n')

        for import_str in module_imports:
            imports[import_str] += 1

    with open(os.path.join(output_dir, 'imports-tally.csv'), 'w') as f:
        for k,v in imports.items():
            f.write(k + ', ' + str(v) + '\n')


if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)
    output_directory = os.path.join("../", output_path)
    analyse_imports(input_directory, output_directory)
