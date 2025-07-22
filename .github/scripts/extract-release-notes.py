#!/usr/bin/env python3
"""
Extract release notes from CHANGELOG.md.

This script extracts the content of the first section (latest release)
from CHANGELOG.md and saves it to release-notes.md.
"""

import sys


def extract_latest_release_notes(changelog_path: str, output_path: str) -> None:
    """Extract the latest release notes from CHANGELOG.md."""
    try:
        with open(changelog_path, 'r') as file:
            changelog = file.read()
        
        output = ''
        inside_subsection = False
        
        for line in changelog.splitlines():
            is_h2 = line.startswith('## ')
            
            if not inside_subsection and is_h2:
                # Found the first H2 section (latest release)
                inside_subsection = True
            elif inside_subsection and not is_h2:
                # Content of the release section
                output += line + '\n'
            elif inside_subsection:
                # Found the next H2 section, stop here
                break
        
        # Write the extracted content
        with open(output_path, 'w') as file:
            file.write(output.strip() + '\n')
        
        print(f"Successfully extracted release notes to {output_path}")
        
    except FileNotFoundError:
        print(f"Error: {changelog_path} not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    extract_latest_release_notes('./CHANGELOG.md', './release-notes.md')