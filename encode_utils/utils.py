# -*- coding: utf-8 -*-

###
# © 2018 The Board of Trustees of the Leland Stanford Junior University
# Nathaniel Watson
# nathankw@stanford.edu
###

"""
Contains utilities that don't require authorization on the DCC servers.
"""

import hashlib
import json
import logging
import os
import requests
import subprocess
import pdb

import encode_utils as eu


#: Stores the HTTP headers to indicate JSON content in a request. 
REQUEST_HEADERS_JSON = {'content-type': 'application/json'}

#: A descendent logger of the debug logger created in `encode_utils`
#: (see the function description for `encode_utils._create_debug_logger`)
DEBUG_LOGGER = logging.getLogger(eu.DEBUG_LOGGER_NAME + "." + __name__)
#: A descendent logger of the error logger created in `encode_utils`
#: (see the function description for `encode_utils._create_error_logger`)
ERROR_LOGGER = logging.getLogger(eu.ERROR_LOGGER_NAME + "." + __name__)


def calculate_md5sum(file_path):
  """"Calculates the md5sum for a file.

  Args:
      file_path: `str`. The path to a local file.

  Returns:
      `str`: The md5sum.
  """
  m = hashlib.md5()
  m.update(open(file_path,'rb').read())
  return m.hexdigest()

def print_format_dict(dico,indent=2):
  """Formats a dictionary for printing purposes to ease visual inspection.

  Wraps the json.dumps() function.

  Args:
      indent: `int`. The number of spaces to indent each level of nesting. Passed directly
          to the json.dumps() method.
  """
  #Could use pprint, but that looks too ugly with dicts due to all the extra spacing.
  return json.dumps(dico,indent=indent,sort_keys=True)

def clean_alias_name(self,alias):
  r"""
  Removes unwanted characters from the alias name. Only the '/' character purportedly causes issues.
  This function replaces both '/' and '\\\\' with '_'. Can be called prior to registering a new
  alias if you know it may contain such unwanted characters. You would then need to update 
  your payload with the new alias to submit.

  Args:
      alias: `str`. A alias that you want to submit.

  Returns:
      `str`: The cleaned alias.
  """
  alias = alias.replace("/","_")
  alias = alias.replace("\\","_")
  return alias

def create_subprocess(cmd,check_retcode=True):
  """Runs a command in a subprocess and checks for any errors.

  Creates a subprocess via a call to subprocess.Popen with the argument 'shell=True', and pipes
  stdout and stderr.  

  Args:
      cmd: `str`. The command to execute.
      check_retcode: `bool`. When True, then an `subprocess.SubprocessError` is raised when the 
        subprocess returns a non-zero return code. 
        The error message will display the command that was executed along with its
        actual return code,  as well as any messages that the subprocess sent to STDOUT and STDERR.
        When False, the `subprocess.Popen` instance will be returned instead and it is expected 
        that the caller will call the its `communicate` method.

  Returns:
      Two-item tuple containing the subprocess's STDOUT and STDERR streams' content if 
      `check_retcode=True`, otherwise a `subprocess.Popen` instance.

  Raises:
      subprocess.SubprocessError: There is a non-zero return code and `check_retcode=True`.
  """
  popen = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if check_retcode:
    stdout,stderr = popen.communicate()
    stdout = stdout.strip()
    stderr = stderr.strip()
    retcode = popen.returncode
    if retcode:
      #subprocess.SubprocessError was introduced in Python 3.3.
      raise subprocess.SubprocessError(
        ("subprocess command '{cmd}' failed with returncode '{returncode}'.\n\nstdout is:"
         " '{stdout}'.\n\nstderr is: '{stderr}'.").format(cmd=cmd,returncode=retcode,stdout=stdout,stderr=stderr))
    return stdout,stderr
  else:
    return popen

def strip_alias_prefix(self,alias):
  """
  Splits 'alias' on ':' to strip off any alias prefix. Aliases have a lab-specific prefix with
  ':' delimiting the lab name and the rest of the alias; this delimiter shouldn't appear
  elsewhere in the alias.

  Args:
      alias: `str`. The alias.

  Returns:
      `str`: The alias without the lab prefix.

  **Example**:: 

          strip_alias_prefix("michael-snyder:B-167")
          # Returns "B-167"

  """
  return name.split(":")[-1]

def add_to_set(self,entries,new):
  """Adds an entry to a list and makes a set for uniqueness before returning the list.

  Args:
      entries: `list`.
      new: (any datatype) The new member to add to the list.

  Returns:
      `list`: A deduplicated list.
  """
  entries.append(new)
  unique_list = list(set(entries))
  return unique_list

def does_lib_replicate_exist(lib_accession,exp_accession,biologicial_replicate_number=False,technical_replicate_number=False):
  """
  Regarding the replicates on the specified experiment, determines whether any of them belong
  to the specified library.  Optional constraints are the biologicial_replicate_number and
  the technical_replicate_number props of the replicates.

  Args:
      lib_accession: `str`. The value of a library object's 'accession' property.
      exp_accession: `str`. The value of an experiment object's accession. The lib_accession
        should belong to a replicate on this experiment.
      biologicial_replicate_number: int. The biological replicate number.
      technical_replicate_number: int. The technical replicate number.

  Returns:
      `list`: The replicates that pass the search constraints.
  """
  biologicial_replicate_number = int(biologicial_replicate_number)
  technical_replicate_number = int(technical_replicate_number)
  results = []
  for rep in replicates_json_from_dcc:
    rep_id = rep["uuid"]
    if not lib_accession == rep["library"]["accession"]:
      continue
    if biologicial_replicate_number:
      if biologicial_replicate_number != rep["biological_replicate_number"]:
        continue
    if technical_replicate_number:
      if technical_replicate_number != rep["technical_replicate_number"]:
        continue
    results.append(rep)
  return results
