#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
# © 2023 IGVF-DACC
# Jin wook Lee
# leepc12@stanford.edu (or gmail.com)
###

"""
Use this script to export Terra's table to TSV.
"""

import argparse
from igvf_utils.terra import (
    get_default_workspace_name,
    get_default_workspace_namespace,
    get_terra_table_json,
    get_terra_table_tsv,
)
import json


DEFAULT_JSON_INDENT = 2


def get_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-t", "--terra-table-name", required=True, help="""
        Terra workspace's table name."""
    )

    parser.add_argument(
        "-b", "--terra-workspace-namespace", required=False, help="""
        Terra workspace namespace (billing account name).""",
        default=get_default_workspace_namespace()
    )

    parser.add_argument(
        "-n", "--terra-workspace-name", required=False, help="""
        Terra workspace name.""",
        default=get_default_workspace_name()
    )

    parser.add_argument(
        "--tsv", required=False, action="store_true", help="""
        Change output format to TSV."""
    )

    parser.add_argument(
        "-o", "--outfile", required=True, help="""
        The output JSON/TSV file. Format is JSON by default.
        To change to TSV, use --tsv."""
    )

    return parser


def main():
    """Program
    """
    parser = get_parser()
    args = parser.parse_args()

    if args.tsv:
        table_tsv = get_terra_table_tsv(
            args.terra_workspace_namespace,
            args.terra_workspace_name,
            args.terra_table_name,
        )
        out_str = table_tsv
    else:
        table_json = get_terra_table_json(
            args.terra_workspace_namespace,
            args.terra_workspace_name,
            args.terra_table_name,
        )
        out_str = json.dumps(table_json, indent=DEFAULT_JSON_INDENT)

    outfile = args.outfile

    fout = open(outfile, 'w')
    fout.write(out_str)
    fout.close()


if __name__ == "__main__":
    main()
