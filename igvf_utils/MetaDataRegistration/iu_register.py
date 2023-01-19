#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
# © 2018 The Board of Trustees of the Leland Stanford Junior University
# Nathaniel Watson
# nathankw@stanford.edu
###

"""
Given a tab-delimited or JSON input file containing one or more records belonging to one of the profiles
listed on the IGVF Portal (such as https://igvfd-dev.demo.igvf.org/profiles/document.json),
either POSTS or PATCHES the records. The default is to POST each record; to PATCH instead, see
the ``--patch`` option.

When POSTING file records, the md5sum of each file will be calculated for you if you haven't
already provided the `md5sum` property. Then, after the POST operation completes, the actual file
will be uploaded to AWS S3. In order for this to work, you must set the `submitted_file_name`
property to the full, local path to your file to upload. Alternatively, you can set
`submitted_file_name` to and existing S3 object, i.e. s3://mybucket/reads.fastq.

Note that there is a special 'trick' defined in the ``igvf_utils.connection.Connection()``
class that can be taken advantage of to simplify submission under certain profiles.
It concerns the `attachment` property in any profile that employs it, such as the `document`
profile.  The trick works as follows: instead of constructing the `attachment` propery object
value as defined in the schema, simply use a single-key object of the following format::

  {"path": "/path/to/myfile"}

and the `attachment` object will be constructed for you.

|
"""

import argparse
import json
import os
import re
import sys
import requests

import igvf_utils.utils as iuu
import igvf_utils.connection as iuc
from igvf_utils.parent_argparser import igvf_login_parser
from igvf_utils.profiles import Profiles

# Check that Python3 is being used
v = sys.version_info
if v < (3, 3):
    raise Exception("Requires Python 3.3 or greater.")

#: RECORD_ID_FIELD is a special field that won't be skipped in the create_payload() function.
#: It is used when patching objects to indicate the identifier of the record to patch.
RECORD_ID_FIELD = "record_id"


def get_parser():
    parser = argparse.ArgumentParser(
        description = __doc__,
        parents=[igvf_login_parser],
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-d", "--dry-run", action="store_true", help="""
    Set this option to enable the dry-run feature, such that no modifications are performed on the
    IGVF Portal.  This is useful if you'd like to inspect the logs or ensure the validity of
    your input file.""")

    parser.add_argument("--no-aliases", action="store_true", help="""
    Setting this option is NOT advised. Set this option for doing a POST when your input file 
    doesn't contain an 'aliases' column, even though this property is supported in the corresponding
    IGVF profile.
    When POSTING a record to a profile that includes the 'aliases' property, this package requires
    the 'aliases' property be used for traceability purposes and because without this property, 
    it'll be very easy to create duplicate objects on the Portal.  For example, you can easily 
    create the same biosample as many times as you want on the Portal when not providing an alias.""")

    parser.add_argument(
        "--no-upload-file",
        action="store_true",
        help="Don't upload files when POSTing file objects",
    )

    parser.add_argument("-p", "--profile_id", required=True, help="""
    The ID of the profile to submit to, i.e. use 'document' for
    https://igvfd-dev.demo.igvf.org/profiles/document.json. The profile will be pulled down for
    type-checking in order to type-cast any values in the input file to the proper type (i.e. some
    values need to be submitted as integers, not strings).""")

    parser.add_argument("-i", "--infile", required=True, help="""
    The JSON input file or tab-delimited input file. 

    **The tab-delimited file format:**
    Must have a field-header line as the first line.
    Any lines after the header line that start with a '#' will be skipped, as well as any empty lines.
    The field names must be exactly equal to the corresponding property names in the corresponding 
    profile. Non-scematic fields are allowed as long as they begin with a '#'; they will be 
    skipped. If a property has an array data type (as indicated in the profile's documentation 
    on the Portal), the array literals '[' and ']' are optional. Values within the array must 
    be comma-delimited. For example, if a property takes an array of strings, then you can use 
    either of these as the value:

    1) str1,str2,str3
    2) [str1,str2,str3]

    On the other hand, if a property takes a JSON object as a value, then the value you enter must be
    valid JSON. This is true anytime you have to specify a JSON object. Thus, if you are submitting a
    genetic_modification and you have two 'introduced_tags' to provide, you can supply them in either
    of the following two ways:

    1) {"name": "eGFP", "location": "C-terminal"},{"name": "FLAG","C-terminal"}
    2) [{"name": "eGFP", "location": "C-terminal"},{"name": "FLAG","C-terminal"}]

    **The JSON input file**
    Can be a single JSON object, or an array of JSON objects. Key names must match property names of
    an IGVF record type (profile).

    **The following applies to either input file formats**
    When patching objects, you must specify the 'record_id' field to indicate the identifier of the record.
    Note that this a special field that is not present in the IGVF schema, and doesn't use the '#'
    prefix to mark it as non-schematic. Here you can specify any valid record identifier
    (i.e. UUID, accession, alias).

    Some profiles (most) require specification of the 'award' and 'lab' attributes. These may be set
    as fields in the input file, or can be left out, in which case the default values for these
    attributes will be pulled from the environment variables DCC_AWARD and DCC_LAB, respectively.
    """)

    parser.add_argument("-w", "--overwrite-array-values", action="store_true", help="""
    Only has meaning in combination with the --patch option. When this is specified, it means that
    any keys with array values will be overwritten on the IGVF Portal with the corresponding value
    to patch. The default action is to extend the array value with the patch value and then to remove
    any duplicates.""")

    parser.add_argument("-r", "--remove-property", help="""
    Only has meaning in combination with the --rm-patch option. Properties specified in this argument
    will be popped from the record fetched from the IGVF portal. Can specify as comma delimited
    string.""")

    group = parser.add_mutually_exclusive_group()

    group.add_argument("--patch", action="store_true", help="""
    Presence of this option indicates to PATCH an existing DCC record rather than register a new one.""")

    group.add_argument("--rm-patch", action="store_true", help="""
    Presence of this option indicates to remove a property, as specified by the -r argument,
    from an existing DCC record, and then PATCH it with the payload specified in -i.""")

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.rm_patch and not args.remove_property:
        parser.error("No properties to remove were specified. Use --patch if only patching is needed.")
    if args.remove_property and not args.rm_patch:
        parser.error("Properties to remove were specified, but --rm-patch flag was not set.")

    profile_id = args.profile_id
    igvf_mode = args.igvf_mode
    dry_run = args.dry_run
    no_aliases = args.no_aliases
    overwrite_array_values = args.overwrite_array_values

    conn = iuc.Connection(igvf_mode, dry_run)

    # Put conn into submit mode:
    conn.set_submission(True)

    schema = conn.profiles.get_profile_from_id(profile_id)
    infile = args.infile
    patch = args.patch
    rmpatch = args.rm_patch
    if args.remove_property is not None:
        props_to_remove = args.remove_property.split(",")

    gen = create_payloads(schema=schema, infile=infile)
    for payload in gen:
        if not patch and not rmpatch:
            conn.post(
                payload,
                require_aliases=not no_aliases,
                upload_file=not args.no_upload_file,
            )
        elif rmpatch:
            record_id = payload.get(RECORD_ID_FIELD, False)
            if not record_id:
                raise ValueError(
                    "Can't patch payload {} since there isn't a '{}' field indicating an identifier for the record to be PATCHED.".format(
                        iuu.print_format_dict(payload), RECORD_ID_FIELD))
            payload.pop(RECORD_ID_FIELD)
            payload.update({conn.ENCID_KEY: record_id})
            conn.remove_and_patch(props=props_to_remove, patch=payload, extend_array_values=not overwrite_array_values)
        elif patch:
            record_id = payload.get(RECORD_ID_FIELD, False)
            if not record_id:
                raise ValueError(
                    "Can't patch payload {} since there isn't a '{}' field indicating an identifier for the record to be PATCHED.".format(
                        iuu.print_format_dict(payload), RECORD_ID_FIELD))
            payload.pop(RECORD_ID_FIELD)
            payload.update({conn.ENCID_KEY: record_id})
            conn.patch(payload=payload, extend_array_values=not overwrite_array_values)


def check_valid_json(prop, val, row_count):
    """
    Runs json.loads(val) to ensure valid JSON.

    Args:
        val: str. A string load as JSON.
        prop: str. Name of the schema property/field that stores the passed in val.
        row_count: int. The line number from the input file that is currently being processed.

    Raises:
        ValueError: The input is malformed JSON.
    """

    # Don't try to break down the individual pieces of a nested object. That will be too complex for this script, and will also
    # be too complex for the end user to try and represent in some flattened way. Thus, require the end user to supply proper JSON
    # for a nested object.
    try:
        json_val = json.loads(val)
        if isinstance(json_val, list):
            for item in json_val:
                if not isinstance(item, dict):
                    raise ValueError
    except ValueError:
        print("Error: Invalid JSON in field '{}', row '{}'".format(prop, row_count))
        raise
    return json_val


def typecast(field_name, value, data_type, line_num):
    """
    Converts the value to the specified data type. Used to convert string representations of integers
    in the input file to integers, and string representations of booleans to booleans.

    Args:
        field_name: The name of the field in the input file whose value is being potentially typecast.
            Used only in error messages. 
        value: The value to potentially typecast.
        data_type: Specifies the data type of field_name as indicated in the IGVF profile. 
        line_num: The current line number in the input file. Used only in error messages. 
    """
    if data_type == "integer":
        return int(value)
    elif data_type == "number":
        # JSON Schema says that a number can by any numeric type.
        # First check if integer, if not, treat as float. 
        try:
            return int(value) 
        except ValueError:
            # This will be raised if trying to convert a string representation of a float to an int.
            return float(value)
    elif data_type == "boolean":
        value = value.lower() 
        if value not in ["true", "false"]:
            raise Exception("Can't convert value '{}' in field '{}' on line {} to data type '{}'.".format(value, field_name, line_num, data_type))
        value = json.loads(value)
    return value


def create_payloads(schema, infile):
    """
    First attempts to read the input file as JSON. If that fails, tries the TSV parser.

    Args:
        schema: `IgvfSchema`. The schema of the objects to be submitted.
    """
    try:
        with open(infile) as f:
            payloads = json.load(f)
        return create_payloads_from_json(schema, payloads)
    except ValueError:
        return create_payloads_from_tsv(schema, infile)


def create_payloads_from_json(schema, payloads):
    """
    Generates payloads from a JSON file

    Args:
        schema: `IgvfSchema`. The schema of the objects to be submitted.
        payloads: dict or list parsed from a JSON input file.

    Yields: dict. The payload that can be used to either register or patch the
    metadata for each row.
    """
    if isinstance(payloads, dict):
        payloads = [payloads]
    for payload in payloads:
        payload[iuc.Connection.PROFILE_KEY] = schema.name
        yield payload


def create_payloads_from_tsv(schema, infile):
    """
    Generates the payload for each row in 'infile'.

    Args:
        schema: IgvfSchema. The schema of the objects to be submitted.
        infile - str. Path to input file.

    Yields  : dict. The payload that can be used to either register or patch the metadata for each row.
    """
    STR_REGX = re.compile(r'\'|"')
    # Fetch the schema from the IGVF Portal so we can set attr values to the
    # right type when generating the payload (dict).
    schema_props = [prop.name for prop in schema.properties]
    field_index = {}
    fh = open(infile, 'r')
    header_fields = fh.readline().strip("\n").split("\t")
    skip_field_indices = []
    fi_count = -1  # field index count
    for field in header_fields:
        fi_count += 1
        if field.startswith("#"):  # non-schema field
            skip_field_indices.append(fi_count)
            continue
        if field not in schema_props:
            if field != RECORD_ID_FIELD:
                raise Exception(
                    f"Unknown field name '{field}', which is not registered as a property in the specified schema at {schema.name}.")
        field_index[fi_count] = field

    line_count = 1  # already read header line
    for line in fh:
        line_count += 1
        line = line.strip("\n")
        if not line.strip() or line[0].startswith("#"):
            continue
        line = line.split("\t")
        payload = {}
        payload[iuc.Connection.PROFILE_KEY] = schema.name
        fi_count = -1
        for val in line:
            fi_count += 1
            if fi_count in skip_field_indices:
                continue
            val = val.strip()
            if not val:
                # Then skip. For ex., the biosample schema has a 'date_obtained' property, and if that is
                # empty it'll be treated as a formatting error, and the Portal will return a a 422.
                continue
            field = field_index[fi_count]
            if field == RECORD_ID_FIELD:
                payload[field] = val
                continue
            field_schema = schema.get_property_from_name(field).schema
            schema_val_type = field_schema["type"]
            if schema_val_type == "object":
                # Must be proper JSON
                val = check_valid_json(field, val, line_count)
            elif schema_val_type == "array":
                item_val_type = field_schema["items"]["type"]
                if item_val_type == "object":
                    # Must be valid JSON
                    # Check if user supplied optional JSON array literal. If not, I'll add it.
                    if not val.startswith("["):
                        val = "[" + val
                    if not val.endswith("]"):
                        val += "]"
                    val = check_valid_json(field, val, line_count)
                else:
                    # User is allowed to enter values in string literals. I'll remove them if I find them,
                    # since I'm splitting on the ',' to create a list of strings anyway:
                    val = STR_REGX.sub("", val)
                    # Remove optional JSON array literal since I'm tokenizing and then converting
                    # to an array regardless.
                    if val.startswith("["):
                        val = val[1:]
                    if val.endswith("]"):
                        val = val[:-1]
                    val = [x.strip() for x in val.split(",")]
                    # Type cast tokens if need be, i.e. to integers:
                    val = [typecast(field_name=field, value=x, data_type=item_val_type, line_num=line_count) for x in val if x]
            else:
                val = typecast(field_name=field, value=val, data_type=schema_val_type, line_num=line_count)
            payload[field] = val
        yield payload


if __name__ == "__main__":
    main()