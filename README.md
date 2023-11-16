pytest-testrail
===============

![](https://github.com/allankp/pytest-testrail/workflows/master/badge.svg)
[![PyPI version](https://badge.fury.io/py/pytest-testrail.svg)](https://badge.fury.io/py/pytest-testrail)
[![Downloads](https://pepy.tech/badge/pytest-testrail)](https://pepy.tech/project/pytest-testrail)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/83b960043527429a8310cced2d8defcb)](https://www.codacy.com/manual/allankp/pytest-testrail?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=allankp/pytest-testrail&amp;utm_campaign=Badge_Grade)

This is a pytest plugin for creating/editing testplans or testruns based on pytest markers.
The results of the collected tests will be updated against the testplan/testrun in TestRail.

Installation
------------

    pip install package.whl

Configuration
-------------

### Config for Pytest tests

Add a marker to the tests that will be picked up to be added to the run.

```python
    from pytest_testrail.plugin import testrail

    @testrail('C1234', 'C5678')
    def test_foo():
        # test code goes here

    # OR	

    from pytest_testrail.plugin import pytestrail

    @pytestrail.case('C1234', 'C5678')
    def test_bar():
        # test code goes here
```

Or if you want to add defects to testcase result:

```python

    from pytest_testrail.plugin import pytestrail

    @pytestrail.defect('PF-524', 'BR-543')
    def test_bar():
        # test code goes here
```

### Config for TestRail

* Settings file template config:

```ini
    [API]
    url = https://yoururl.testrail.net/
    email = user@email.com
    password = <api_key>

    [TESTRUN]
    assignedto_id = 1
    project_id = 2
    suite_id = 3
    plan_id = 4
    description = 'This is an example description'

    [TESTCASE]
    custom_comment = 'This is a custom comment'
```

Or

* Set command line options (see below)

Usage
-----

Basically, the following command will create a testrun in TestRail, add all marked tests to run.
Once the all tests are finished they will be updated in TestRail:

```bash
    py.test --testrail --tr-config=<settings file>.cfg
```

### All available options

| option                         | description                                                                                                                               |
| -------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| --testrail                     | Create and update testruns with TestRail                                                                                                  |
| --tr-config                    | Path to the config file containing information about the TestRail server (defaults to testrail.cfg)                                       |
| --tr-url                       | TestRail address you use to access TestRail with your web browser (config file: url in API section)                                       |
| --tr-email                     | Email for the account on the TestRail server (config file: email in API section)                                                          |
| --tr-password                  | Password for the account on the TestRail server (config file: password in API section)                                                    |
| --tr-testrun-assignedto-id     | ID of the user assigned to the test run (config file:assignedto_id in TESTRUN section)                                                    |
| --tr-testrun-project-id        | ID of the project the test run is in (config file: project_id in TESTRUN section)                                                         |
| --tr-testrun-suite-id          | ID of the test suite containing the test cases (config file: suite_id in TESTRUN section)                                                 |
| --tr-testrun-suite-include-all | Include all test cases in specified test suite when creating test run (config file: include_all in TESTRUN section)                       |
| --tr-testrun-name              | Name given to testrun, that appears in TestRail (config file: name in TESTRUN section)                                                    |
| --tr-testrun-description       | Description given to testrun, that appears in TestRail (config file: description in TESTRUN section)                                      |
| --tr-run-id                    | Identifier of testrun, that appears in TestRail. If provided, option "--tr-testrun-name" will be ignored                                  |
| --tr-plan-id                   | Identifier of testplan, that appears in TestRail (config file: plan_id in TESTRUN section) If provided, option "--tr-testrun-name" will be ignored |
| --tr-version                   | Indicate a version in Test Case result.                                                                                                   |
| --tr-no-ssl-cert-check         | Do not check for valid SSL certificate on TestRail host                                                                                   |
| --tr-close-on-complete         | Close a test plan or test run on completion.                                                                                              |
| --tr-dont-publish-blocked      | Do not publish results of "blocked" testcases in TestRail                                                                                 |
| --tr-skip-missing              | Skip test cases that are not present in testrun                                                                                           |
| --tr-milestone-id              | Identifier of milestone to be assigned to run                                                                                             |
| --tc-custom-comment            | Custom comment, to be appended to default comment for test case (config file: custom_comment in TESTCASE section)                         |

### What was changed/added so far with 2.10.0:


| option                         | description                                                                                                                               |
| -------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| --tr-sort-by-status-id         | Test results are sorted by status_id, so that worst test result of parametrized test becomes final test status in TestRail                |

 * Added ability to extract test case IDs from testrun.


### What was changed/added so far with 2.11.0:

* Added **XFAIL** and **XPASS** testrail tests results. 
Pytest test outcome is always one of “passed”, “failed”, “skipped”
[pytest.CollectReport.outcome](https://docs.pytest.org/en/7.1.x/reference/reference.html?highlight=outcome#pytest.CollectReport.outcome)<br>
Tests with mark **'xfail'**(@pytest.mark.xfail) have such test results:<br>
-- In case test outcome is `skipped` - in testrail we get test results `xfail`. <br>
-- In case test outcome is `passed` - in testrail we get test results `xpass`. <br>

* Changed format of data to send with the request.
* Changed COMMENT_SIZE_LIMIT from 4000 to 7000.
* Removed duplicate newline characters in test result comments for a better visual of the Testrail result.

### What was changed/added so far with 2.12.0:

* from 2.11.0 ~~* Removed duplicate newline characters in test result comments for a better visual of the Testrail result.~~
*  Replaced special characters('>','<', "'", '"' ) in test results comment with Unicode.

### What was changed so far with 2.14.0:

*  Added TESTRAIL_TEST_STATUS_PRIORITY see on Testrail result first failed result in parametrized tests.

### What was changed so far with 2.15.0:

*  Added checks for setup functions(fixtures) result if it is either 'skipped' or 'failed'.

It looks for specific markers associated with the test item: 'skipif' and 'xfail' markers.<br>
-- If no 'skipif' and 'xfail' markers and setup functions(fixtures) result 'failed', the reported result is set to 'failed'.<br>
-- If a 'skipif' marker is found and its argument is (True,), the setup functions(fixtures) reported result is set to 'skipped'.<br>
-- If an 'xfail' marker is found and no 'skipif' marker is present, and the reported result setup functions(fixtures) are 'skipped', the reported result is set to 'failed'.<br>

*  Changed TESTRAIL_TEST_STATUS_PRIORITY to see Skipped results last. 

### What was changed so far with 2.16.0:

*  Added checks for setup functions(fixtures) result if it is either 'skipped' or 'failed' if 'skip' marker is found.

-- If a 'skip' marker is found the setup functions(fixtures) reported result is set to 'skipped'.<br>

* Modified don't publish blocked testcases not only cases from test run, but for all cases.

### What was changed so far with 2.17.0:

*  Added checks for 'add_results_for_cases' endpoint. If payload size > max_size(1 Mb) - the number of test results in payload you 
send with one POST request set to 100.    
