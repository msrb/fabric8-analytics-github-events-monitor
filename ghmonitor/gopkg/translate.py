"""Utility functions for translation of Go packages into Github repositories."""

import re
from requests_html import HTMLSession

GITHUB_REPO_RE = re.compile(r"github.com/(?P<user>[a-zA-Z0-9][ A-Za-z0-9_-]*)"
                            r"/(?P<repo>[a-zA-Z0-9][ A-Za-z0-9_-]*)")

from typing import Union

assert Union


def get_repo_from_random_urn(urn):
    # type: (str) -> Union[str, None]
    """
    Translate Go package urn into Github repo.

    In case the repository is not directly from GitHub, it is possible that there is a way to
    translate the urn into Github repository using some magic from "go get". So just try it.
    """
    session = HTMLSession()
    resp = session.get('https://' + urn + '?go-get=1')
    # Check that the request was successful
    if resp.status_code == 200:
        # Find all 'meta' elements, in case there is not any, it will just return empty list
        meta_elements = resp.html.find('meta')

        def _is_go_import_element(e):
            try:
                return e.attrs['name'] == 'go-import'
            except KeyError:
                return False

        # Filter the list, if it was empty from the beginning, no harm done
        go_import_elements = list(filter(_is_go_import_element, meta_elements))
        if len(go_import_elements) > 0:
            # Finally search for github repository
            try:
                m = GITHUB_REPO_RE.search(go_import_elements[0].attrs['content'])
                if m is not None:
                    return '{}/{}'.format(m.group('user'), m.group('repo'))
            except KeyError:
                pass

    return None


def translate(pkg):
    # type: (str) -> Union[str, None]
    """
    Take whatever `go get` takes and return string with organization/user and repository name.

    It returns none for anything that is not available on Github.
    """
    if pkg == "":
        return None

    # Test if the pkg is directly from github
    m = GITHUB_REPO_RE.match(pkg)
    if m is not None:
        return '{}/{}'.format(m.group('user'), m.group('repo'))

    # Test if the pkg name can be translated into Github repo
    repo = get_repo_from_random_urn(pkg)
    if repo is not None:
        return repo

    return None
