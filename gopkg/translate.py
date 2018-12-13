import re
from requests_html import HTMLSession

GITHUB_REPO_RE = re.compile(r"github.com/(?P<user>[a-zA-Z0-9][ A-Za-z0-9_-]*)"
                            r"/(?P<repo>[a-zA-Z0-9][ A-Za-z0-9_-]*)")


def get_repo_from_random_urn(urn):
    session = HTMLSession()
    resp = session.get('https://' + urn + '?go-get=1')
    if resp.status_code == 200:
        meta_elements = resp.html.find('meta')

        def _is_go_import_element(e):
            return e.attrs['name'] == 'go-import'

        go_import_elements = list(filter(_is_go_import_element, meta_elements))
        if len(go_import_elements) > 0:
            m = GITHUB_REPO_RE.search(go_import_elements[0].attrs['content'])
            if m is not None:
                return '{}/{}'.format(m.group('user'), m.group('repo'))

    return None


def translate(pkg):
    """
    Takes whatever `go get` takes and return string with organization/user and repository name.
    It returns none for anything that is not available on Github.
    """
    m = GITHUB_REPO_RE.match(pkg)
    if m is not None:
        return '{}/{}'.format(m.group('user'), m.group('repo'))

    repo = get_repo_from_random_urn(pkg)
    if repo is not None:
        return repo

    return None


def test_get_repo_urn():
    assert 'kubernetes/metrics' == get_repo_from_random_urn('k8s.io/metrics')

def test_github_re():
    assert GITHUB_REPO_RE.match('bitbucket.com/user/repo') is None
    m = GITHUB_REPO_RE.match('github.com/user/project')
    assert m.group('user') == 'user'
    assert m.group('repo') == 'project'
    m = GITHUB_REPO_RE.match('github.com/user/project/folder')
    assert m.group('user') == 'user'
    assert m.group('repo') == 'project'


def test_translate():
    assert 'kubernetes/metrics' == translate('k8s.io/metrics')
    assert 'user/project' == translate('github.com/user/project')
    assert translate('launchpad.net/project') is None

