# Mining NLP Repositories 

Research on mining NLP repositories. 

# Steps to Run

**Clone this repository**

#Install Docker
If docker is not present 

Link to install ( [docker install] https://docs.docker.com/v17.12/install/#supported-platforms )

# Datasets
We have two directories input and output folders.

The research datasets needs to be put into the input folder.

This will be mounted at runtime.

# GitHub Access Token

Go to https://github.com/settings/tokens/new to generate a new token with the perimissions `public_repo` and `read:packages`, and update `mining_nlp_repositories/github.py` with your `ACCESS_TOKEN`.

# Tasks

* To list all tasks 

    `doit list`
    
* Build the docker image

    `doit build`
    
* Fetch project meta-data from GitHub (requires GitHub Access Token)

    `doit fetch_data_science_projects`

* Extract metrics (requires repos in `input` directory):

    `doit analyse_imports`
    `doit analyse_2to3`
    `doit analyse_pylint`
    `doit analyse_radon_cc`

* Remove the docker image
    
    `doit remove`

