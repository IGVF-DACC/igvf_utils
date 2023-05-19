#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
# © 2018 The Board of Trustees of the Leland Stanford Junior University
# Nathaniel Watson
# nathankw@stanford.edu
###

"""
Tests functions in the ``igvf_utils.terra`` module.
"""

import json
import os
from unittest import mock

import pytest

import igvf_utils.tests
from igvf_utils import terra


# mock os.environ
@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(
        os.environ,
        {
            terra.ENV_VAR_WORKSPACE_NAME: "TEST_WORKSPACE_NAME",
            terra.ENV_VAR_WORKSPACE_NAMESPACE: "TEST_WORKSPACE_NAMESPACE"
        }
    ):
        yield


def test_get_default_workspace_name():
    assert terra.get_default_workspace_name() == "TEST_WORKSPACE_NAME"


def test_get_default_workspace_namespace():
    assert terra.get_default_workspace_namespace() == "TEST_WORKSPACE_NAMESPACE"


@pytest.mark.parametrize(
    "input,expected",
    [
        ('{"a" : 1} ', True),
        (' ["a",1,{"b":2}]', True),
        ('  [{}]  ', True),
        ('    {[{}]}    ', True),
        ('abcd', False),
        ('not a json string', False),
        ('[] b', False),
        ('a {}', False),
    ],
)
def test_is_json_string(input, expected):
    assert terra.is_json_string(input) == expected


class MockResponse:
    """get_entities_response obtained from
    https://app.terra.bio/#workspaces/DACC_ANVIL/test_checkfiles_wdl/data
    """
    content = b"[{\"attributes\":{\"test_str_array\":\"[\\\"a\\\",\\\"b\\\",3]\",\"md5sum\":\"2976d268d837c81bc77bacdbd5b28cbf\",\"output_type\":\"fastq\",\"test_array\":{\"itemsType\":\"AttributeValue\",\"items\":[\"1\",\"2\",\"a\",\"b\",\"c\"]},\"file\":\"gs://encode-pipeline-test-samples/encode-atac-seq-pipeline/ENCSR356KRQ/fastq_subsampled/rep2/pair1/ENCFF641SFZ.subsampled.400.fastq.gz\",\"file_type\":\"read\"},\"entityType\":\"file\",\"name\":\"1\"},{\"attributes\":{\"test_str_array\":\"[\\\"x\\\",\\\"b\\\",3]\",\"md5sum\":\"xxxxxx\",\"output_type\":\"asdfasdf\",\"test_array\":{\"itemsType\":\"AttributeValue\",\"items\":[\"1\",\"2\",\"a\",\"b\",\"c\"]},\"file\":\"asdf\",\"file_type\":\"fdsa\"},\"entityType\":\"file\",\"name\":\"2\"}]"
    def raise_for_status():
        pass


EXPECTED_JSON=[
  {
    "test_str_array": [
      "a",
      "b",
      3
    ],
    "md5sum": "2976d268d837c81bc77bacdbd5b28cbf",
    "output_type": "fastq",
    "test_array": [
      "1",
      "2",
      "a",
      "b",
      "c"
    ],
    "file": "gs://encode-pipeline-test-samples/encode-atac-seq-pipeline/ENCSR356KRQ/fastq_subsampled/rep2/pair1/ENCFF641SFZ.subsampled.400.fastq.gz",
    "file_type": "read"
  },
  {
    "test_str_array": [
      "x",
      "b",
      3
    ],
    "md5sum": "xxxxxx",
    "output_type": "asdfasdf",
    "test_array": [
      "1",
      "2",
      "a",
      "b",
      "c"
    ],
    "file": "asdf",
    "file_type": "fdsa"
  }
]


EXPECTED_TSV="""test_str_array\tmd5sum\toutput_type\ttest_array\tfile\tfile_type
['a', 'b', 3]\t2976d268d837c81bc77bacdbd5b28cbf\tfastq\t['1', '2', 'a', 'b', 'c']\tgs://encode-pipeline-test-samples/encode-atac-seq-pipeline/ENCSR356KRQ/fastq_subsampled/rep2/pair1/ENCFF641SFZ.subsampled.400.fastq.gz\tread
['x', 'b', 3]\txxxxxx\tasdfasdf\t['1', '2', 'a', 'b', 'c']\tasdf\tfdsa
"""


def test_get_terra_table_json(mocker, mocked_object=MockResponse, expected_json=EXPECTED_JSON):
    mocker.patch(
        "firecloud.api.get_entities",
        return_value=mocked_object,
    )
    assert terra.get_terra_table_json("test", "test", "test") == expected_json


def test_get_terra_table_tsv(mocker, mocked_object=MockResponse, expected_tsv=EXPECTED_TSV):
    mocker.patch(
        "firecloud.api.get_entities",
        return_value=mocked_object,
    )
    assert terra.get_terra_table_tsv("test", "test", "test") == expected_tsv
