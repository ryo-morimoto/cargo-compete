#!/usr/bin/env python3
"""
Resolve crate versions from crates.io API.

This script queries the crates.io API to find the latest version of a crate
that matches the given version requirement pattern.
"""

from argparse import ArgumentParser
import json
import urllib.request
import re

CRATE_SPEC = re.compile(r'\A([a-zA-Z0-9_-]+)@\^([0-9]+)\.([0-9]+)\Z')


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('specs', metavar='PSEUDO_SPECS', type=CrateSpec, nargs='+')
    print('\n'.join(map(resolve, parser.parse_args().specs)))


class CrateSpec:
    def __init__(self, s: str):
        if not (m := CRATE_SPEC.match(s)):
            raise RuntimeError(f'the version must be `{CRATE_SPEC.pattern}`')
        self.package_name = m.group(1)
        self.version_req_major = int(m.group(2))
        self.version_req_minor = int(m.group(3))


def resolve(spec: CrateSpec) -> str:
    with urllib.request.urlopen(f'https://crates.io/api/v1/crates/{spec.package_name}') as res:
        versions = json.load(res)['versions']
    matched = set()
    for version in versions:
        major, minor, patch_pre_build = version['num'].split('.')
        major, minor = (int(major), int(minor))
        if ((major, spec.version_req_major) == (0, 0) and minor == spec.version_req_minor or major == spec.version_req_major and minor >= spec.version_req_minor) and patch_pre_build.isdecimal():
            matched.add((minor, int(patch_pre_build)))
    if not matched:
        raise RuntimeError(f'No such package: `{spec.package_name} ^{spec.version_req_major}.{spec.version_req_minor}`')
    minor, patch = max(matched)
    return f'{spec.package_name}={spec.version_req_major}.{minor}.{patch}'


if __name__ == '__main__':
    main()