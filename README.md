# Mining Data Science Repositories 

Research on mining Data Science repositories. 

# Steps to Run

**Figshare:** Extract contents of [results.tar.gz](https://doi.org/10.6084/m9.figshare.12377237.v2) to `output` directory, then jump to _Analyse results (in Jupyter)_ section.

**From scratch:** Clone this repository then follow steps below to identify, clone, and analyse the repositories.

# Install Docker
If docker is not present 

Link to install ([docker install](https://docs.docker.com/v17.12/install/#supported-platforms))

# Datasets
We have four directories: `data`, `input_drive`, `input`, and `output`:

* The `data` folder holds project metadata fetched from GitHub (97 MB, committed to this Git repo for convenience)

* The `input_drive` folder is for the cloned repositories (4.6 TB in total, so we suggest using a network storage drive)

* The `symlink_input` task will create symlinks within the `input` folder to the `input_drive`.

* The `output` directory holds metrics and the final analysis results (2 GB when compressed, shared on Figshare).

# GitHub Access Token

Go to https://github.com/settings/tokens/new to generate a new token with the perimissions `public_repo` and `read:packages`, and update `mining_nlp_repositories/github.py` with your `ACCESS_TOKEN`.

# Tasks

* To list all tasks 

    `surround run list`

* Build the docker image

    `surround run build`

* Fetch project meta-data from GitHub (requires GitHub Access Token)

    ```
    surround run fetch_data_science_projects
    surround run fetch_non_data_science_projects
    ```

* Clone projects from GitHub

    ```
    surround run clone_data_science_projects
    surround run clone_non_data_science_projects
    ```

    Move `data/boa/cloned-repos` to `input_drive/cloned-repos/boa`

    Move `data/non-data-science/cloned-repos` to `input_drive/cloned-repos/non-data-science`

    Manually create `input_drive/cloned-repos/boa-zip-download` and extract any unclonable DS repos here

    Manually create `input_drive/cloned-repos/non-data-science-zip-download` and extract any unclonable non-DS repos here

* Specify list of repositories to extract metrics for

    Run `notebooks/create-lists-to-extract.ipynb` notebook and move results from `data/selected` to `input_drive/selected`

    Manually modify lists as needed. E.g. `repo_ids_ds_chunk_000801-001552_filt.csv` excludes repo `858127` as it contains a file that causes Pylint to hang indefinitely.

* Populate input directory with symlinks (requires repos in `input_drive` directory)

    `surround run symlink_input`

* Extract metrics (requires `input` directory to be populated)

    ```
    surround run analyse_imports
    surround run analyse_2to3
    surround run analyse_pylint
    surround run analyse_radon_cc
    surround run analyse_loc
    surround run analyse_git
    ```

    Each of the analyse tasks support an optional argument to limit the list of repositories analysed, e.g. `surround run analyse_pylint input/repos-ids.csv` (useful for splitting up large jobs). If not provided, all repos will be analysed.

    The exact commands used are listed below. Due to a limitation of Surround (Issue #230) it was necessary to call `doit` directly in order to run multiple Surround tasks simultaneously:

    ```
    mkdir -p output/ds-t1; nohup time doit --backend sqlite3 analyse_2to3 --args "input_drive/selected/repo_ids_full_ds.csv output/ds-t1" > output/ds-t1/nohup.out &
    mkdir -p output/ds-t2; nohup time doit --backend sqlite3 analyse_imports --args "input_drive/selected/repo_ids_full_ds.csv output/ds-t2" > output/ds-t2/nohup.out &
    mkdir -p output/ds-t3; nohup time doit --backend sqlite3 analyse_radon_cc --args "input_drive/selected/repo_ids_full_ds.csv output/ds-t3" > output/ds-t3/nohup.out &
    # Skipped: Takes 302 hours:
    # mkdir -p output/ds-t4; nohup time doit --backend sqlite3 analyse_radon_raw --args "input_drive/selected/repo_ids_full_ds.csv output/ds-t4" > output/ds-t4/nohup.out &
    mkdir -p output/ds-t5; nohup time doit --backend sqlite3 analyse_version --args "input_drive/selected/repo_ids_full_ds.csv output/ds-t5" > output/ds-t5/nohup.out &
    mkdir -p output/ds-t6; nohup time doit --backend sqlite3 analyse_loc --args "input_drive/selected/repo_ids_full_ds.csv output/ds-t6" > output/ds-t6/nohup.out &
    mkdir -p output/ds-t7; nohup time doit --backend sqlite3 analyse_git --args "input_drive/selected/repo_ids_full_ds.csv output/ds-t7" > output/ds-t7/nohup.out &
    
    mkdir -p output/nonds-t1; nohup time doit --backend sqlite3 analyse_2to3 --args "input_drive/selected/repo_ids_full_nonds.csv output/nonds-t1" > output/nonds-t1/nohup.out &
    mkdir -p output/nonds-t2; nohup time doit --backend sqlite3 analyse_imports --args "input_drive/selected/repo_ids_full_nonds.csv output/nonds-t2" > output/nonds-t2/nohup.out &
    mkdir -p output/nonds-t3; nohup time doit --backend sqlite3 analyse_radon_cc --args "input_drive/selected/repo_ids_full_nonds.csv output/nonds-t3" > output/nonds-t3/nohup.out &
    # Skipped: Hangs indefinitely on repo 67065438:
    # mkdir -p output/nonds-t4; nohup time doit --backend sqlite3 analyse_radon_raw --args "input_drive/selected/repo_ids_full_nonds.csv output/nonds-t4" > output/nonds-t4/nohup.out &
    mkdir -p output/nonds-t5; nohup time doit --backend sqlite3 analyse_version --args "input_drive/selected/repo_ids_full_nonds.csv output/nonds-t5" > output/nonds-t5/nohup.out & 
    mkdir -p output/nonds-t6; nohup time doit --backend sqlite3 analyse_loc --args "input_drive/selected/repo_ids_full_nonds.csv output/nonds-t6" > output/nonds-t6/nohup.out &
    mkdir -p output/nonds-t7; nohup time doit --backend sqlite3 analyse_git --args "input_drive/selected/repo_ids_full_nonds.csv output/nonds-t7" > output/nonds-t7/nohup.out &

    mkdir -p output/ds-chunk11; nohup time doit --backend sqlite3 analyse_pylint --args "input_drive/selected/repo_ids_ds_chunk_000001-000800.csv output/ds-chunk11" > output/ds-chunk11/nohup.out &
    # Revised: Hangs indefinitely on repo 858127:
    # mkdir -p output/ds-chunk2; nohup time doit --backend sqlite3 analyse_pylint --args "input_drive/selected/repo_ids_ds_chunk_000801-001552.csv output/ds-chunk2" > output/ds-chunk2/nohup.out &
    mkdir -p output/ds-chunk13; nohup time doit --backend sqlite3 analyse_pylint --args "input_drive/selected/repo_ids_ds_chunk_000801-001552_filt.csv output/ds-chunk13" > output/ds-chunk13/nohup.out &

    mkdir -p output/nonds-chunk11; nohup time doit --backend sqlite3 analyse_pylint --args "input_drive/selected/repo_ids_nonds_chunk_000001-000800.csv output/nonds-chunk11" > output/nonds-chunk11/nohup.out &
    mkdir -p output/nonds-chunk12; nohup time doit --backend sqlite3 analyse_pylint --args "input_drive/selected/repo_ids_nonds_chunk_000801-001600.csv output/nonds-chunk12" > output/nonds-chunk12/nohup.out &
    mkdir -p output/nonds-chunk13; nohup time doit --backend sqlite3 analyse_pylint --args "input_drive/selected/repo_ids_nonds_chunk_001601-002400.csv output/nonds-chunk13" > output/nonds-chunk13/nohup.out &
    mkdir -p output/nonds-chunk14; nohup time doit --backend sqlite3 analyse_pylint --args "input_drive/selected/repo_ids_nonds_chunk_002401-002511.csv output/nonds-chunk14" > output/nonds-chunk14/nohup.out &

    ```

    Each command takes between 1 hour (LOC over DS repos) to 52 hours (Pylint over chunk of 800 repos), and may consume up to 8GB of memory each. (We assigned ~4 concurrent tasks to each node)

# Analyse results (in Jupyter):

* Merge the chunks back together (results will be written to `output/merged`):
   ```
   merge_chunks-cc.ipynb
   merge_chunks-imports.ipynb
   merge_chunks.ipynb
   merge_chunks-loc.ipynb
   merge_chunks-version.ipynb
   merge_chunks-git.ipynb
   ```

* Analyse project imports and Python version (intermediate results, will be written to `output/notebooks_out`):
   ```
   analyse_imports.ipynb
   analyse_py_ver.ipynb
   ```

* Refine the final selection of DS and non-DS repos to control for the distribution of stars, age, etc.:
   ```
   distributions-sel.ipynb
   ```

   Analyse differences between the final selection of DS versus non-DS repos:
   ```
   ml-distribution.ipynb
   ```

* Tables and figures for the paper will be exported to `output/notebooks_out`

* Remove the docker image

    `surround run remove`

# Known Bugs

* The GitHub API pages results, thus the number of contributors is limited to 30, so this should be interpreted as 30+. This does not affect the figure in the paper (as the axis is limited to 30)
* The old project name was `mining_nlp_repositories`, as we initially trailed the analysis on a corpus of NLP projects. The new project name `Mining Data Science Repositories` reflects the broader scope of the project to include all types of DS repositories (but the source code still contains references to the old project name).


