Forked from https://github.com/StanfordBioinformatics/encode_utils (2022-04-27).


# Introduction

Tools that are useful to any IGVF Consortium submitting group, as well as the general community working with IGVF data.  Library and scripts are coded in Python.

See the [wiki](https://github.com/IGVF-DACC/igvf_utils/wiki) to get started. 

API and script documentation are available on [Read the Docs](http://igvf-utils.readthedocs.io/).

# Installation
Please clone this repository (e.g. `git clone git@github.com:IGVF-DACC/igvf_utils.git`) and then refer to instructions on the [Installation wiki page](https://github.com/IGVF-DACC/igvf_utils/wiki/Installation).

# Installation on Terra platfrom

Create a new workspace and link it to a proper billing account. On the workspace UI, click on a cloud-shaped icon on the right sidebar and create a new Jupyter notebook terminal.

Run the followings to install this tool and its dependencies.
```bash
pip install igvf_utils
```

This tool will automatically grab workspace name and billing project name from environment variables `WORKSPACE_NAME` and `WORKSPACE_NAMESPACE`, respectively. These environment variables are automatically set by default on Terra's Jupyter notebook instance. You can directly edit these variables to change them.

```bash
./iu_register.py ... --terra-table-name TERRA_TABLE_NAME # --terra-workspace-name X --terra-workspace-namespace Y
```

You can also export Terra workspace's table to a JSON file.
```bash
./iu_get_terra_table.py --terra-table-name TERRA_TABLE_NAME -o out.json
```

# How to access to Terra on a local computer

Follow [this instruction](https://github.com/IGVF-DACC/terra-billing-alert#install-firecloud) to install FireCloud and register your Google service account to Terra. Make sure to add the service account email address to workspace's AD and read/write permissions on workspace's share page.
