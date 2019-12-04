import os
from surround import Config
from pylint.epylint import lint
import sys
import json
import csv
parser = json.JSONDecoder()

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']


def data_reader_from_text(file_name, list_name):
    with open(file_name) as f:
        data = f.read()
        head = 0
    while True:
        head = (data.find('{', head) + 1 or data.find('[', head) + 1) - 1
        try:
            struct, head = parser.raw_decode(data, head)
            list_name.append(struct)
        except (ValueError, json.JSONDecodeError):
            break
    return list_name


if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)
    files = []
    parsed = []
    if os.path.exists(input_directory):
        for r, d, f in os.walk(input_directory):
            for file in f:
                if file.endswith(".py"):
                    files.append(os.path.join(r, file))
        
        lst = [file for file in files]
        repository_list = []
        output_directory = os.path.join("../", output_path)
        sys.stdout = open(os.path.join(output_directory, "text_output.txt"), 'w')
        for i in lst:
            repository_list.append(i.split('/', 3)[2])
            lint(i, ['--output-format', 'json'])
        sys.stdout.close()
        parsed = data_reader_from_text(os.path.join(output_directory, "text_output.txt"), parsed)
        key_list = []
        for key in parsed[0]:
            key_list.append(key)
            f = csv.writer(open(os.path.join(output_directory, 'structured.csv'), "w"))
            f.writerow(key_list)
        for index, record in enumerate(parsed):
            current_record = []
            for key in key_list:
                current_record.append(record[key])
            f.writerow(current_record)