"""
Utility functions to manage an import graph
"""

import pandas as pd
import numpy as np
import logging
import warnings

logging.basicConfig(filename='importgraph.log', level=logging.DEBUG)
log = logging.getLogger('importgraph')


def strip_init(mod, end=".__init__"):
    if pd.isnull(mod):
        return mod
    if mod.endswith(end):
        return mod[:-len(end)]
    return mod


def path_sort_key(path_name):
    if pd.isnull(path_name):
        return (np.inf, path_name)
    depth = path_name.count("/")
    # prefer paths with least depth, then alphabetical
    return (depth, path_name)


def sanitize_modules(paths2imports):
    """
    If two paths refer to the same module, drop the longer of the paths
    """
    dups = paths2imports.copy()

    rows = []    
    for module_name, pathrows in dups.groupby('module_name'):
        paths = pd.unique(pathrows['path'])
        sortedpaths = sorted(paths, key=path_sort_key)

        if len(sortedpaths) == 0:
            continue

        preferred_path = sortedpaths[0]
        importrows = pathrows[pathrows["path"] == preferred_path]
        rows.append(importrows)

    sanitized = pd.concat(rows)
    return sanitized.sort_index()


def analyse_project(module2imports, module2hops_init):
    module2hops = module2hops_init
    
    while True:
        module2hops_prev = module2hops.copy()
        # to join import names to module names, will need to first strip off any ".__init__" in module name
        module2hops["module_name"] = module2hops["module_name"].map(strip_init)

        # Use Pandas to lookup join last known hop distance for each module import
        merged = module2imports.merge(module2hops,
            how="left",
            left_on="import_name",
            right_on="module_name",
            suffixes=("_m", "_h")
            #validate="one_to_many" # TODO: Re-enable validation
        )

        # Update the hop distance of the module to be the minimum of its imports (+1)
        min_hops = merged[["module_name_m", "hops"]].groupby("module_name_m").agg('min')
        min_hops["hops"] = min_hops["hops"] + 1
        # Flatten/reset index and change columns to match original names
        # As left join, order (hopefully) won't change -- this is later verified by an asssertion that the module names are identical 
        module2hops = pd.DataFrame(min_hops.to_records()).rename(columns={"module_name_m": "module_name"})
        module2hops = module2hops.fillna(np.inf)
        
        # Check if hops reduced (if not, retain initial hop distance)
        module2hops["hops"] = np.where(module2hops["hops"] < module2hops_prev["hops"], module2hops["hops"], module2hops_prev["hops"])

        # module names should not change
        assert module2hops["module_name"].equals(module2hops_prev["module_name"])

        # iterate until hops converges
        if module2hops["hops"].equals(module2hops_prev["hops"]):
            break

    return module2hops


def matches(imp, lib):
    if pd.isnull(imp):
        return False
    if lib == imp:
        return True
    if imp.startswith(lib + "."):
        return True
    return False


def matches_any(imp, libs):
    for lib in libs:
        if matches(imp, lib):
            return True
    return False


def seedhops(modules2imports, tier0modules):
    set_modules = set(modules2imports["module_name"])
    tier1 = modules2imports["import_name"].apply(lambda x: matches_any(x, tier0modules))
        
    if modules2imports.empty:
        # workaround disappearing column names issue when dataframe is empty
        tier1modules = set()
    else:
        tier1modules = set(modules2imports[tier1]["module_name"])
    other_modules = set_modules - tier1modules - set([np.nan])
    # Set hops to 0 for any of the tier0modules seeds
    tier1rows = [[m, 0] for m in tier1modules]
    # For others initialize hops as inf
    other_rows = [[m, np.inf] for m in other_modules]
    rows = tier1rows + other_rows
    module2hops_init = pd.DataFrame(rows, columns=["module_name", "hops"])
    
    return module2hops_init.sort_values(by = "module_name").reset_index(drop = True)


def paths2modules(path2imports):
    # Grab just the module and import names
    modules2imports = path2imports[["module_name", "import_name"]]
    set_modules = set(modules2imports["module_name"])
    # Drop empty ("") modules imports (these will be added back later)
    modules2imports = modules2imports[~pd.isnull(modules2imports["import_name"])]
    modules2imports = modules2imports.drop_duplicates()
    # Add back empty module imports only if no other imports
    empty = set_modules - set(modules2imports["module_name"]) - set([np.nan])
    rows_empty = pd.DataFrame([[m, np.nan] for m in empty], columns=["module_name", "import_name"])
    modules2imports = pd.concat([modules2imports, rows_empty])
    
    return modules2imports.sort_values(by = "module_name").reset_index(drop = True)


def modules2paths(
    module2hops,
    # optionally consume mapping X from paths2modules
    paths2imports):
    merged = paths2imports.merge(module2hops,
        how="left",
        left_on="module_name",
        right_on="module_name")
        
    path2hops = merged[["path", "module_name", "hops"]]
    path2hops = path2hops.drop_duplicates()
    
    # Detect errors arising from paths that share the same module_name.
    # Pre-process with sanitize_modules(...) to ensure this does not happen.
    is_unique = path2hops["module_name"][~pd.isnull(path2hops["module_name"])].is_unique

    # TODO: Remove this, and just do an assertion insted
    if not is_unique:
        # TODO: pass the repo name in for logging purposes.
        # As a workaround, extract it from (first) path
        repo = path2hops["path"].iloc[0].split("/")[0]
        # TODO: Create easy means to log this to a table
        warnings.warn("Duplicate module name: {}".format(repo), RuntimeWarning)

    # Can optionally disable this, but results may be misleading,
    # as if multiple paths have the same module name, they may end up with each other's results.
    assert is_unique
    
    return path2hops.sort_values(by = "path").reset_index(drop = True)


def process_repo(paths2imports, tier0modules):
    module2imports = paths2modules(paths2imports)
    module2hops_init = seedhops(module2imports, tier0modules)
    module2hops = analyse_project(module2imports, module2hops_init)
    path2hops = modules2paths(module2hops, paths2imports)

    return path2hops


# Block of code to:
# Iterate over project repos in dataframe:
#     Run analyse_project
# Stitch all results together into a combined dataframe
def process_repos(repo_paths2imports, tier0modules):
    results = []
    for repo, repo_data in repo_paths2imports.groupby("repo"):
        repo_res = process_repo(repo_data[["path", "module_name", "import_name"]], tier0modules)
        repo_res["repo"] = repo
        results.append(repo_res)
    
    return pd.concat(results)
