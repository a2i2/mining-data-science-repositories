import os
import subprocess
from surround import Config
#from pylint.epylint import lint
import sys
import json
import csv
import logging

logging.basicConfig(filename='../debug.log',level=logging.DEBUG)

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

def lint(filepath, out_f, py_version='python3'):
    result = subprocess.run([py_version, '-m', 'pylint', '--output-format', 'json', filepath], stdout=out_f, stderr=subprocess.PIPE)
    #result_stdout = result.stdout.decode('utf-8')
    result_stderr = result.stderr.decode('utf-8')
    logging.info(result_stderr)
    #return result_stdout

def run_pylint(py_version):
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
        txt_out_fname = os.path.join(output_directory, "text_output_" + py_version + ".txt")
        with open(txt_out_fname, 'w') as out_f:
            for i in lst:
                repository_list.append(i.split('/', 3)[2])
                lint(i, out_f, py_version)
        parsed = data_reader_from_text(txt_out_fname, parsed)
        key_list = []
        for key in parsed[0]:
            key_list.append(key)
            f = csv.writer(open(os.path.join(output_directory, "structured_" + py_version + ".csv"), "w"))
            f.writerow(key_list)
        for index, record in enumerate(parsed):
            current_record = []
            for key in key_list:
                current_record.append(record[key])
            f.writerow(current_record)

if __name__ == "__main__":
    run_pylint("python2")
    run_pylint("python3")
