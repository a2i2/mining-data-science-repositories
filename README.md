# Mining NLP Repositories 

Research on mining NLP repositories. 

# Steps to Run

**Clone this repository**

# Install Docker
If docker is not present 

Link to install ( [docker install] https://docs.docker.com/v17.12/install/#supported-platforms )

# Datasets
We have three directories: input_drive, input, and output folders.

The research datasets needs to be put into the input_drive folder.

This will be mounted at runtime.

The symlink_input task will symlink repos found within the input_drive to the input folder.

# GitHub Access Token

Go to https://github.com/settings/tokens/new to generate a new token with the perimissions `public_repo` and `read:packages`, and update `mining_nlp_repositories/github.py` with your `ACCESS_TOKEN`.

# Tasks

* To list all tasks 

    `surround run list`
    
* Build the docker image

    `surround run build`
    
* Fetch project meta-data from GitHub (requires GitHub Access Token)

    `surround run fetch_data_science_projects`

* Populate input directory with symlinks (requires repos in `input_drive` directory):

    `surround run symlink_input`

* Extract metrics (requires `input` directory to be populated):

    ```
    surround run analyse_imports
    surround run analyse_2to3
    surround run analyse_pylint
    surround run analyse_radon_cc
    ```
    
    Each of the analyse tasks support an optional argument to limit the list of repositories analysed, e.g. `surround run analyse_pylint input/repos-ids.csv` (useful for splitting up large jobs). If not provided, all repos will be analysed.
    

* Remove the docker image
    
    `surround run remove`

