Examples
========

Imports
-------

::

  import igvf_utils as iu
  from igvf_utils.connection import Connection

Connecting to the production and development Portals
----------------------------------------------------
You'll need to instantiate the ``Connection`` class, passing in a value for the ``igvf_mode``
argument.

::

  #prod portal:
  conn = Connection("prod")

  #dev portal
  conn = Connection("dev")

You can provide a custom host name as well, such as a demo host, granted that you have access to
it::

  conn = Connection("igvfd-dev.demo.igvf.org/")

Dry Runs
^^^^^^^^
The second argument, ``dry_run``, can be set to ``True``, which allows you to test things out
without worrying about any IGVF Portal modifications being made::

  conn = Connection("dev",True)

The logging will indicate that you are in dry-run mode. Once you are happy with the simulation, 
you can switch to live-run mode - the default when ``dry_run`` isn't set::

  conn.set_live_run()

And you can even switch back to dry-run mode::

  conn.set_dry_run()


Log Files
---------
Each time you create a new ``Connection`` object, either directly as show above, or indirectly
through use of the packaged scripts, a log directory by the name of `IU_LOGS` will be created in the
calling directory.  Three log files are created:

  1. A debug log file that contains all of STDOUT.
  2. An error log file that contains only terse error messages. This is your first stop for checking
     to see if any errors occurred. Anything that is written to this file is also written to STDOUT,
     hence the debug log as well.
  3. A POST log file, which only logs new records that are successfully added to the IGVF Portal.
     Everything written to this file is also written to STDOUT, hence the debug log as well.

These log files are specific to the host that you connect to. Each host will have a different trio
of logs, with the host name included in the log file names. 

GET Request
-----------

Retrieve the JSON serialization for the record with accession IGVFSM9352WYNZ::

  conn.get("IGVFSM9352WYNZ")

Search
------

Search for ChIP-seq assays performed on primary cells from blood::

  query = {
      "assay_title": "ChIP-seq",
      "biosample_type": "primary cell",
      "organ_slims": "blood",
      "type": "Experiment"
  }

  conn.search(query)

The query will be URL encoded for you. If you want to use the search functionality 
programmatically, you should first test your search interactively on the Portal. The result will 
be an array of record results, where each result is given in its JSON representation.

PATCH Request
-------------

Add a new alias to the Tissue record IGVFSM0000ABCD. Create a payload
(`dict`) that indicates the record to PATCH and the new alias. The record to PATCH must be
indicated by using the non-schematic key `Connection.IGVFID_KEY`, or `self.IGVFID_KEY` from the
perspective of a `Connection` instance, which will be removed from the payload prior to submission:

::

  payload = {
      conn.IGVFID_KEY: "IGVFSM0000ABCD",
      "aliases": ["new-alias"]
    }
    
  conn.patch(payload)

File Upload
-----------

Given the File record IGVFFI2246NBHO, say that we need to upload the corresponding FASTQ file to AWS
(i.e. maybe the former attempt failed at the time of creating the File record). Here's how to
do it:

::

  conn.upload_file(file_id="IGVFFI2246NBHO")

This will only work if the File record has the `submitted_file_name` property set, which is
interpreted as the local path to the file to submit.
You can also explicitly set the path to the file to upload:

::

  conn.upload_file(file_id="IGVFFI2246NBHO",file_path="/path/to/myfile")

POST Request
------------

Let's create a new Sample record on the Portal:

::

  payload = {
    "aliases": [
        "igvf:brain_sample_01"
    ],
    "biosample_term": "/sample-terms/UBERON_0000955/",
    "disease_terms": [
        "/phenotype-terms/MONDO_0004975/"
    ],
    "donors": [
        "/rodent-donors/IGVFDO930TRK/"
    ],
    "source": "/sources/j-michael-cherry/",
    "status": "released",
    "taxa": "Mus musculus"
  }

Notice that we didn't specify the required `award` and `lab` properties (required by the IGVF
profiles). When not specified, the defaults will be taken from the environment variables 
`IGVF_AWARD` and `IGVF_LAB` when present. Otherwise, you will get an error when trying to submit.
Before we can POST this though, we need to indicate the profile of the record-to-be.

Specifying the profile key
^^^^^^^^^^^^^^^^^^^^^^^^^^

We are almost ready to hand this payload over to the `post()` method, however, we need to first
indicate the profile to POST to. To do this, add a special key to your payload that is stored in 
the constant `Connection.PROFILE_KEY`.  The `post()` method depends on this key as the way of
indicating which profile to create a new record under. There are a few ways in which you can
specify the profile, but the recommended way is to use the stripped-down profile ID. If you 
look at the JSON schema for the File profile at 
https://www.encodeproject.org/profiles/file.json, you'll find that the value of it's `id` 
property is `"/profiles/file.json"`. The stripped-down value that you should use is `file`. 
Another way to say it is to use the barebones profile name that you put in the URL to get to it.
See the documentation in the `profile.Profile` class for further details on how this works.

Without futher ado, let's now add the profile specification to the payload and POST it::

  payload[Connection.PROFILE_KEY] = "file"
  conn.post(payload)

The logging to STDOUT and your log files will indicate the progress of your request, including
the upload of your FASTQ file to AWS.

Removing properties from a record
---------------------------------

This feature is implemented via the PUT HTTP method, which works by replacing the existing record 
on the Portal with a new representation. You just need to specify a list of property names to be removed.
A GET on the record is first made with the query parameter ``frame=edit``, and the properties that
you indicate for removal are popped out of the returned JSON representation of the record. This
updated JSON representation is then sent to the Portal via a PUT operation.

For example, say you have a biosample record and you want to remove the `pooled_from` property.
This property stores a list of other biosample records. You can't just empty out the list interactively
in the Portal, or programmatically via a PATCH operation since this property, when present, can't be
empty. This is where the PUT HTTP method comes in handy. Let's look at an example::

  conn = Connection("dev")
  conn.remove_props(rec_id="IGVFSM8899STAN",props=["pooled_from"])

It's as simple as that. It should be mentioned that the ``remove_props()`` method will do some validation
of its own to ensure that you aren't trying to delete something that you really shouldn't delete,
such as properties that are:

  1. required,
  2. read-only, and
  3. non-submittable. 

as indicated in the profile (JSON schema) of the record of interest. The Portal would most likely
reject or silently ignore any attempt to remove such properties, nonetheless, to be a good citizen,
this client performs these checks regardless for good measure.
