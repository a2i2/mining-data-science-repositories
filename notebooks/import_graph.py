"""
Utility functions to manage an import graph
"""

import pandas as pd
import numpy as np


def strip_init(mod, end=".__init__"):
    if mod.endswith(end):
        return mod[:-len(end)]
    return mod


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
            suffixes=("_m", "_h"),
            validate="one_to_many")
        
        # Update the hop distance of the module to be the minimum of its imports (+1)
        min_hops = merged[["module_name_m", "hops"]].groupby("module_name_m").agg('min')
        min_hops["hops"] = min_hops["hops"] + 1
        # Flatten/reset index and change columns to match original names
        # As left join, order (hopefully) won't change -- this is later verified by an asssertion that the module names are identical 
        module2hops = pd.DataFrame(min_hops.to_records()).rename(columns={"module_name_m": "module_name"})
        module2hops = module2hops.fillna(np.inf)

        # Check if hops reduced (if not, retain initial hop distance)
        module2hops["hops"] = np.where(module2hops["hops"] < module2hops_prev["hops"], module2hops["hops"], module2hops_prev["hops"])
                
        cmp = (module2hops == module2hops_prev).all()
        assert cmp["module_name"] # module names should not change
        
        # iterate until hops converges
        if cmp["hops"]:
            break

    return module2hops


def matches(imp, lib):
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
    tier1modules = set(modules2imports[tier1]["module_name"])
    other_modules = set_modules - tier1modules
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
    modules2imports = modules2imports[modules2imports["import_name"] != ""]
    modules2imports = modules2imports.drop_duplicates()
    # Add back empty module imports only if no other imports
    empty = set_modules - set(modules2imports["module_name"])
    rows_empty = pd.DataFrame([[m, ""] for m in empty], columns=["module_name", "import_name"])
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
    
    # Detect errors arising from paths that share the same module_name (ideally should not happen)
    assert path2hops["module_name"].is_unique
    
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
# Stitch results into new "hops" col of dataframe
def process_repos(repo_paths2imports, tier0modules):
    results = []
    for repo, repo_data in repo_paths2imports.groupby("repo"):
        repo_res = process_repo(repo_data[["path", "module_name", "import_name"]], tier0modules)
        repo_res["repo"] = repo
        results.append(repo_res)
    
    return pd.concat(results)
