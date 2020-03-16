import os
import subprocess
from surround import Config
import shlex

CONFIG = Config(os.path.dirname(__file__))
DOIT_CONFIG = {'verbosity':2}
PACKAGE_PATH = os.path.basename(CONFIG["package_path"])
IMAGE = "%s/%s:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
DOCKER_VOLUME_PATH = ["--volume", "%s/input:/app/input" % CONFIG["volume_path"],
                      "--volume", "%s/output:/app/output" % CONFIG["volume_path"],
                      "--volume", "{0}/{1}:/app/{1}".format(CONFIG["volume_path"], PACKAGE_PATH)]
DOCKER_VOLUME_PATH_STRING = ' '.join(shlex.quote(arg) for arg in DOCKER_VOLUME_PATH)

PARAMS = [
    {
        'name': 'args',
        'long': 'args',
        'type': str,
        'default': ""
    }
]

def task_build():
    """Build the Docker image for the current project"""
    return {
        'actions': ['docker build --tag=%s .' % IMAGE],
        'params': PARAMS
    }


def task_remove():
    """Remove the Docker image for the current project"""
    return {
        'actions': ['docker rmi %s -f' % IMAGE],
        'params': PARAMS
    }


def task_analyse_pylint():
    """Run the analyse pylint task for the project"""
    return {
        'actions': ["docker run -w /app/%s %s %s python3 task_analyse_pylint.py %s" % (PACKAGE_PATH, DOCKER_VOLUME_PATH_STRING, IMAGE, "%(args)s")],
        'params': PARAMS
    }


def task_analyse_radon_raw():
    """Run the analyse radon raw task for the project"""
    return {
        'actions': ["docker run -w /app/%s %s %s python3 task_analyse_radon_raw.py %s" % (PACKAGE_PATH, DOCKER_VOLUME_PATH_STRING, IMAGE, "%(args)s")],
        'params': PARAMS
    }


def task_analyse_radon_cc():
    """Run the analyse radon cc task for the project"""
    return {
        'actions': ["docker run -w /app/%s %s %s python3 task_analyse_radon_cc.py %s" % (PACKAGE_PATH, DOCKER_VOLUME_PATH_STRING, IMAGE, "%(args)s")],
        'params': PARAMS
    }


def task_analyse_version():
    """Run the analyse version task for the project"""
    return {
        'actions': ["docker run -w /app/%s %s %s python3 task_analyse_version.py %s" % (PACKAGE_PATH, DOCKER_VOLUME_PATH_STRING, IMAGE, "%(args)s")],
        'params': PARAMS
    }


def task_analyse_imports():
    """Run the analyse imports task for the project"""
    return {
        'actions': ["docker run -w /app/%s %s %s python3 task_analyse_imports.py %s" % (PACKAGE_PATH, DOCKER_VOLUME_PATH_STRING, IMAGE, "%(args)s")],
        'params': PARAMS
    }


def task_analyse_2to3():
    """Run the analyse 2to3 task for the project"""
    return {
        'actions': ["docker run -w /app/%s %s %s python3 task_analyse_2to3.py %s" % (PACKAGE_PATH, DOCKER_VOLUME_PATH_STRING, IMAGE, "%(args)s")],
        'params': PARAMS
    }


def task_fetch_data_science_projects():
    """Fetch project meta-data from GitHub"""
    return {
        'actions': ["docker run --volume \"%s/\":/app %s python3 ./%s/task_fetch_data_science_projects.py %s" % (CONFIG["volume_path"], IMAGE, PACKAGE_PATH, "%(args)s")],
        'params': PARAMS
    }

def task_clone_data_science_projects():
    """Run the explore task for the project"""
    return {
        'actions': ["docker run --volume \"%s/\":/app %s python3 ./%s/task_clone_data_science_repos.py %s" % (CONFIG["volume_path"], IMAGE, PACKAGE_PATH, "%(args)s")],
        'params': PARAMS
    }

def task_fetch_non_data_science_projects():
    """Run the explore task for the project"""
    return {
        'actions': ["docker run --volume \"%s/\":/app %s python3 ./%s/task_fetch_non_data_science_projects.py %s" % (CONFIG["volume_path"], IMAGE, PACKAGE_PATH, "%(args)s")],
        'params': PARAMS
    }


def task_interactive():
    """Run the Docker container in interactive mode"""
    def run():
        process = subprocess.Popen(['docker', 'run', '-it', '--rm', '-w', '/app'] + DOCKER_VOLUME_PATH + [IMAGE, 'bash'], encoding='utf-8')
        process.wait()

    return {
        'actions': [run]
    }


def task_prod():
    """Run the Docker container used for packaging """
    return {
        'actions': ["docker run %s %s" % (DOCKER_VOLUME_PATH_STRING, IMAGE)],
        'task_dep': ["build"],
        'params': PARAMS
    }
