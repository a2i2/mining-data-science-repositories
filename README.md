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


# Tasks

* To list all tasks 

    `doit list`
    
* Build the docker image

    `doit build`
    
* Run the docker image (only py-lint command for now)

    `doit prod`
    
* Remove the docker image
    
    `doit remove`

