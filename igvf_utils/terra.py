# -*- coding: utf-8 -*-

###
# © 2023 IGVF-DACC
# Jin wook Lee
# leepc12@stanford.edu (or gmail.com)
###

"""
Contains utilities that communicate with Terra's FireCloud Python REST API
"""

from firecloud import api
from pandas import DataFrame
import json
import logging
import os


ENV_VAR_WORKSPACE_NAME="WORKSPACE_NAME"
ENV_VAR_WORKSPACE_NAMESPACE="WORKSPACE_NAMESPACE"



class TerraError(Exception):
    pass


class TerraErrorTableNotFound(TerraError):
    pass


def get_default_workspace_name():
    return os.environ.get(ENV_VAR_WORKSPACE_NAME)


def get_default_workspace_namespace():
    return os.environ.get(ENV_VAR_WORKSPACE_NAMESPACE)


def get_terra_table_json(workspace_namespace, workspace_name, table_name):
    """
    Get Terra workspace's table in a JSON format.
    Such table is called entities and each row in a table is called entity.
    See https://api.firecloud.org/#/Entities/downloadEntitiesTSV for details.

    Terra returns an empty contents with status_code 200.

    Args:
        workspace_namespace: `str`. Terra billing project name.
        workspace_name: `str`. Terra workspace name.
        table_name: `str`. Workspace's table name (called entity_type in their API).

    Returns:
        `dict`: JSON excluding Terra table's primary/unique key (marked as "entity:" in their table).

    Raises:
        `HTTPError `: Reraised from Terra's REST API.
        `TerraErrorTableNotFound `: Raise if table does not exist.
    """
    response = api.get_entities(workspace_namespace, workspace_name, table_name)
    response.raise_for_status()

    org_data = json.loads(response._content.decode())

    if not org_data:
        raise TerraErrorTableNotFound

    # parse contents to exclude a primary key
    parsed = []
    for entity in org_data:
        parsed.append(entity["attributes"])

    return parsed


def get_terra_table_tsv(workspace_namespace, workspace_name, table_name):
    """
    Get Terra workspace's table in TSV string.

    Args:
        workspace_namespace: `str`. Terra billing project name.
        workspace_name: `str`. Terra workspace name.
        table_name: `str`. Workspace's table name (called entity_type in their API).

    Returns:
        `str`: TSV string excluding Terra table's primary/unique key (marked as "entity:" in their table).

    Raises:
        `HTTPError `: Reraised from Terra's REST API.
        `TerraErrorTableNotFound `: Raise if table does not exist.
    """
    table_json = get_terra_table_json(workspace_namespace, workspace_name, table_name)

    table = DataFrame.from_dict(table_json)
    return table.to_csv(sep="\t", index=False)
