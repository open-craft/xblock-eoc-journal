End of Course Journal XBlock
============================

The "End of Course" Journal XBlock provides ability for a participant to download his/her activity once he/she completes
the course.  Currently only [problem-builder](https://github.com/open-craft/problem-builder) freeform answers are supported.

This XBlock also displays a summary of the learner's participation, proficiency, and engagement in the course compared
with the course averages.

Installation
------------

Install the requirements into the Python virtual environment of your `edx-platform` installation by running the
following command from the root folder:

```bash
$ pip install -e .
```

Enabling in Studio
------------------

You can enable the EOC Journal XBlock in Studio through the Advanced Settings.

1. From the main page of a specific course, navigate to `Settings -> Advanced Settings` from the top menu.
2. Check for the `Advanced Module List` policy key, and add `"eoc-journal"` to the policy value list.
3. Click the "Save changes" button.

Testing
-------

Inside a fresh virtualenv, `cd` into the root folder of this repository (`xblock-eoc-journal`) and run:

```bash
$ pip install -U pip wheel
$ pip install -r requirements-test.txt
$ pip install -r $VENV/src/xblock-sdk/requirements/base.txt
$ pip install -r $VENV/src/xblock-sdk/requirements/test.txt
```

`$VENV` is your fresh virtual environment root directory.

You can then run the entire test suite via

```bash
$ python run_tests.py
```

Note that you need a compatible version of Firefox installed to be able to run integration tests. Recent versions of
Firefox are not currently supported by the selenium driver that we are using. If your default Firefox installation
doesn't work, you can install Firefox 43 which is known to be compatible somewhere on your disk, and then set the
`SELENIUM_FIREFOX_PATH` environment variable to point to your custom Firefox 43 installation.
