#!/usr/bin/env python3
''' Publish test results to the GitHub job summary and as inline annotations.

- Job summary ($GITHUB_STEP_SUMMARY): overall + per-file pass/fail table and
  the coverage one-liner, rendered in the run's "Summary" tab and the PR
  check popup.
- Annotations (::error file=...::): one per failed test, shown inline on the
  PR diff, linter-style.

Safe to run outside GitHub Actions: without GITHUB_STEP_SUMMARY it only
prints the table to stdout, and missing files are a no-op.
'''
import os
import xml.etree.ElementTree as ET
from collections import OrderedDict

JUNIT_FILE = 'pytest_results.xml'
COVERAGE_FILE = 'coverage_summary.txt'


def parse_junit(path):
    ''' Return a list of (module, test, result) tuples. '''
    tests = []
    for tc in ET.parse(path).getroot().iter('testcase'):
        module = tc.get('classname', '')
        name = tc.get('name', '')
        failure = tc.find('failure')
        error = tc.find('error')
        skipped = tc.find('skipped')
        if failure is not None or error is not None:
            result = 'failed'
        elif skipped is not None:
            result = 'skipped'
        else:
            result = 'passed'
        tests.append((module, name, result))
    return tests


def main():
    if not os.path.exists(JUNIT_FILE):
        print(f'{JUNIT_FILE} not found, nothing to summarize')
        return

    tests = parse_junit(JUNIT_FILE)
    if not tests:
        return

    # Inline annotations, one per failed test (shown on the PR diff).
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        for module, name, result in tests:
            if result == 'failed':
                # module is the test file path without .py, e.g.
                # "tests/pytest_ps4_ds4_controller".
                print(f'::error file={module}.py::{name} failed')

    per_file = OrderedDict()
    for module, name, result in tests:
        per_file.setdefault(module, []).append(result)

    passed = sum(1 for t in tests if t[2] == 'passed')
    failed = sum(1 for t in tests if t[2] == 'failed')
    skipped = sum(1 for t in tests if t[2] == 'skipped')

    lines = [
        '## BlueRetro test suite',
        '',
        f'**{passed} passed**, **{failed} failed**, {skipped} skipped '
        f'({len(tests)} total)',
        '',
        '| Test file | Passed | Failed | Skipped |',
        '|---|---|---|---|',
    ]
    for module, results in per_file.items():
        lines.append(f'| {module} '
                     f'| {results.count("passed")} '
                     f'| {results.count("failed")} '
                     f'| {results.count("skipped")} |')

    # Coverage one-liner, if the gcov step produced one.
    if os.path.exists(COVERAGE_FILE):
        with open(COVERAGE_FILE) as f:
            lines += ['', '## Coverage', '', '```', f.read().rstrip(), '```']

    table = '\n'.join(lines) + '\n'

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as f:
            f.write(table)
    else:
        print(table)


if __name__ == '__main__':
    main()
