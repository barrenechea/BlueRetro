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
SERIAL_LOG = 'serial_log.txt'
PANIC_MARKERS = (b'Guru Meditation Error', b'WDT_SYS_RESET', b'RTCWDT_RTC_RESET')


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


def first_panic(path):
    ''' Return the first firmware panic line in the DUT serial log, or None. '''
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        for line in f:
            if any(m in line for m in PANIC_MARKERS):
                return line.decode(errors='replace').strip()
    return None


def main():
    # A panic at boot stops pytest before any test ran, so the panic has to
    # be reported on its own or the summary would stay silent.
    panic = first_panic(SERIAL_LOG)
    if panic and os.environ.get('GITHUB_ACTIONS') == 'true':
        print(f'::error title=DUT panic::{panic}')

    tests = parse_junit(JUNIT_FILE) if os.path.exists(JUNIT_FILE) else []
    if not tests and not panic:
        print(f'no results in {JUNIT_FILE}, nothing to summarize')
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
    ]
    if panic:
        lines += ['> [!CAUTION]', f'> Firmware panicked, see `{SERIAL_LOG}` in the logs artifact:',
                  f'> `{panic}`', '']
    lines += [
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
