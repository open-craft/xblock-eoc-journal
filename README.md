End of Course Journal XBlock
============================

The "End of Course" Journal XBlock provides ability for a participant to download his/her activity once he/she completes
the course.  Currently only [problem-builder](https://github.com/open-craft/problem-builder) freeform answers are supported.

This XBlock also displays a summary of the learner's participation, proficiency, and engagement in the course compared
with the course averages.

NOTE: While it is called the End of Course Journal, the block can actually be added at any point during the course.

See the [Native API documentation](native-api.md) for access to the student view and student view state data.

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

Translation (i18n)
-------------------------------

This repo offers multiple make targets to automate the translation tasks.
First, install `requirements-test.txt`:

```bash
pip install -r requirements-test.txt
```

Each make target will be explained below:

- `extract_translations`. Use [`i18n_tool` extract](https://github.com/edx/i18n-tools) to create `.po` files based on all the tagged strings in the python and javascript code.
- `compile_translations`. Use [`i18n_tool` generate](https://github.com/edx/i18n-tools) to create `.mo` compiled files.
- `detect_changed_source_translations`. Use [`i18n_tool` changed](https://github.com/edx/i18n-tools) to identify any updated translations.
- `validate_translations`. Compile translations and check the source translations haven't changed.

If you want to add a new language:
  1. Add language to `eoc_journal/translations/config.yaml`
  2. Make sure all tagged strings have been extracted:
  ```bash
  make extract_translations
  ```
  3. Clone `en` directory to `eoc_journal/translations/<lang_code>/` for example: `eoc_journal/translations/fa_IR/`
  4. Make necessary changes to translation files headers. Make sure you have proper `Language` and `Plural-Forms` lines.
  5. When you finished your modification process, re-compile the translation messages.
  ```bash
  make compile_translations
  ```

Transifex
---------

This repo offers different make targets to automate interaction with transifex. To use these make targets first install `requirements-test.txt`.
```bash
pip install -r requirements-test.txt
```

These are the different make targets used to interact with transifex:

- `pull_translations`. Pull translations from Transifex.
- `push_translations`. Push translations to Transifex.

The transifex configuration is stored in `.tx`. For more information read [transifex's documentation](https://docs.transifex.com/client/client-configuration)
