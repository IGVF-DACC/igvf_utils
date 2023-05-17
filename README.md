© 2019 The Board of Trustees of the Leland Stanford Junior University.

# igvf_utils
Tools that are useful to any IGVF Consortium submitting group, as well as the general community working with IGVF data.  Library and scripts are coded in Python.

See the [wiki](https://github.com/IGVF-DACC/igvf_utils/wiki) to get started. 

API and script documentation are available on [Read the Docs](http://igvf-utils.readthedocs.io/).

# Latest news

2022-04-27

Forked from https://github.com/StanfordBioinformatics/encode_utils.

# Installation on Terra platfrom

Create a new workspace and link it to a proper billing account. On the workspace UI, click on a cloud-shaped icon on the right sidebar and create a new Jupyter notebook terminal.

Run the followings to install this tool and its dependencies.
```bash
pip install igvf_utils
```

This tool will automatically grab workspace name and billing project name from environment variables `WORKSPACE_NAME` and `WORKSPACE_NAMESPACE`, respectively. These environment variables are automatically set by default on Terra's Jupyter notebook instance. You can directly edit these variables to change them.

```bash
./iu_register.py ... --terra-table TERRA_TABLE_NAME
```

You can also export Terra workspace's table to a TSV file.
```bash
./iu_get_terra_table.py -t TERRA_TABLE_NAME -o out.tsv
```
