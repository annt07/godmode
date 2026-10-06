"""Offline tests for skills/mr-full-review/scripts/review_request.py.

No network and no real tokens: provider detection is pure, and API calls go
through a fake `http` function that serves canned responses per URL.
Run: uv run --with pytest pytest tests -q
"""
import importlib.util
import pathlib

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skills" / "mr-full-review" / "scripts" / "review_request.py"
spec = importlib.util.spec_from_file_location("review_request", SCRIPT)
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)


@pytest.fixture(autouse=True)
def tokens(monkeypatch):
    for k in ("GITLAB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "BITBUCKET_TOKEN", "BITBUCKET_USERNAME",
              "BITBUCKET_APP_PASSWORD", "GODMODE_GIT_PROVIDERS"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("GITLAB_TOKEN", "glpat-test")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp-test")
    monkeypatch.setenv("BITBUCKET_TOKEN", "bb-test")


# ----------------------------------------------------------------- detection from URLs
@pytest.mark.parametrize("ref, provider, host, project, number", [
    ("https://gitlab.com/carelon/eai/ai-foundry/eval-as-a-service/-/merge_requests/120",
     "gitlab", "gitlab.com", "carelon/eai/ai-foundry/eval-as-a-service", "120"),
    ("https://gitlab.corp.example/team/repo/-/merge_requests/7", "gitlab", "gitlab.corp.example", "team/repo", "7"),
    ("https://github.com/annt07/godmode/pull/3", "github", "github.com", "annt07/godmode", "3"),
    ("https://github.corp.example/org/svc/pull/42", "github", "github.corp.example", "org/svc", "42"),
    ("https://bitbucket.org/ws/repo/pull-requests/9", "bitbucket-cloud", "bitbucket.org", "ws/repo", "9"),
    ("https://bitbucket.corp.example/projects/CLMQ/repos/pricing/pull-requests/15",
     "bitbucket-server", "bitbucket.corp.example", "CLMQ/pricing", "15"),
    ("https://git.corp.example/context/projects/CLMQ/repos/pricing/pull-requests/15/overview",
     "bitbucket-server", "git.corp.example", "CLMQ/pricing", "15"),
])
def test_resolve_from_url(ref, provider, host, project, number):
    t = rr.resolve(ref)
    assert (t.provider, t.host, t.project, t.number) == (provider, host, project, number)


# ----------------------------------------------------------------- detection from remotes
@pytest.mark.parametrize("remote, provider, host, project", [
    ("git@gitlab.com:carelon/eai/repo.git", "gitlab", "gitlab.com", "carelon/eai/repo"),
    ("https://gitlab.com/carelon/eai/repo.git", "gitlab", "gitlab.com", "carelon/eai/repo"),
    ("https://user@github.com/annt07/godmode.git", "github", "github.com", "annt07/godmode"),
    ("git@github.com:annt07/godmode.git", "github", "github.com", "annt07/godmode"),
    ("git@bitbucket.org:ws/repo.git", "bitbucket-cloud", "bitbucket.org", "ws/repo"),
    ("https://bitbucket.corp.example/scm/clmq/pricing.git", "bitbucket-server", "bitbucket.corp.example", "clmq/pricing"),
    ("ssh://git@bitbucket.corp.example:7999/clmq/pricing.git", "bitbucket-server", "bitbucket.corp.example", "clmq/pricing"),
])
def test_resolve_bare_number_from_remote(remote, provider, host, project):
    t = rr.resolve("12", remote_url=remote)
    assert (t.provider, t.host, t.project, t.number) == (provider, host, project, "12")


def test_bang_and_hash_numbers_accepted():
    assert rr.resolve("!12", remote_url="git@gitlab.com:a/b.git").number == "12"
    assert rr.resolve("#12", remote_url="git@github.com:a/b.git").number == "12"


def test_unknown_host_needs_mapping(monkeypatch):
    with pytest.raises(rr.ReviewError, match="can't tell which provider"):
        rr.resolve("5", remote_url="https://code.corp.example/team/repo.git")
    monkeypatch.setenv("GODMODE_GIT_PROVIDERS", "code.corp.example=gitlab")
    assert rr.resolve("5", remote_url="https://code.corp.example/team/repo.git").provider == "gitlab"


def test_provider_override_wins():
    t = rr.resolve("5", provider="gitlab", remote_url="https://code.corp.example/team/repo.git")
    assert t.provider == "gitlab"


def test_mapping_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("GODMODE_GIT_PROVIDERS", "code.corp.example=svn")
    with pytest.raises(rr.ReviewError, match="unknown provider"):
        rr.resolve("5", remote_url="https://code.corp.example/team/repo.git")


# ----------------------------------------------------------------- auth
def test_missing_token_is_a_clear_error(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN")
    with pytest.raises(rr.ReviewError, match="GITHUB_TOKEN"):
        rr.Client(rr.Target("github", "github.com", "a/b", "1"), http=lambda *a: None)


def test_github_accepts_gh_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN")
    monkeypatch.setenv("GH_TOKEN", "x")
    assert "Authorization: Bearer x" in rr.auth_headers("github")


def test_bitbucket_cloud_app_password(monkeypatch):
    monkeypatch.delenv("BITBUCKET_TOKEN")
    monkeypatch.setenv("BITBUCKET_USERNAME", "u")
    monkeypatch.setenv("BITBUCKET_APP_PASSWORD", "p")
    assert rr.auth_headers("bitbucket-cloud") == ["Authorization: Basic dTpw"]


def test_api_bases():
    assert rr.api_base(rr.Target("github", "github.com", "a/b", "1")) == "https://api.github.com"
    assert rr.api_base(rr.Target("github", "ghe.corp", "a/b", "1")) == "https://ghe.corp/api/v3"
    assert rr.api_base(rr.Target("gitlab", "gitlab.corp", "a/b", "1")) == "https://gitlab.corp/api/v4"
    assert rr.api_base(rr.Target("bitbucket-cloud", "bitbucket.org", "a/b", "1")) == "https://api.bitbucket.org/2.0"
    assert rr.api_base(rr.Target("bitbucket-server", "bb.corp", "K/r", "1")) == "https://bb.corp/rest/api/1.0"


# ----------------------------------------------------------------- normalisation with a fake API
def fake(responses):
    calls = []

    def http(url, headers, raw=False):
        calls.append(url)
        for prefix, body in responses.items():
            if url.startswith(prefix):
                return body
        raise AssertionError(f"unexpected URL {url}")
    http.calls = calls
    return http


def test_gitlab_request_comments_and_ci():
    t = rr.Target("gitlab", "gitlab.com", "g/r", "120")
    base = "https://gitlab.com/api/v4/projects/g%2Fr"
    http = fake({
        f"{base}/merge_requests/120/notes": [
            {"id": 2, "author": {"username": "rev"}, "created_at": "2026-01-02", "body": "fix this",
             "system": False, "position": {"new_path": "a.py"}},
            {"id": 1, "author": {"username": "bot"}, "created_at": "2026-01-01", "body": "added 1 commit", "system": True},
        ],
        f"{base}/merge_requests/120/pipelines": [{"id": 5, "status": "failed", "sha": "abcdef1234", "web_url": "u"}],
        f"{base}/merge_requests/120": {"title": "T", "state": "opened", "author": {"username": "dev"},
                                       "source_branch": "feat", "target_branch": "dev", "web_url": "w",
                                       "draft": True, "description": "D", "sha": "abc"},
        f"{base}/pipelines/5/jobs": [{"id": 9, "name": "test", "status": "failed", "allow_failure": False}],
        f"{base}/jobs/9/trace": "line1\nAssertionError",
    })
    c = rr.Client(t, http=http)
    info = rr.fetch_request(c)
    assert (info["source"], info["target"], info["draft"]) == ("feat", "dev", True)
    comments = rr.fetch_comments(c)
    assert [x["id"] for x in comments] == [1, 2] and comments[1]["kind"] == "diff" and comments[1]["path"] == "a.py"
    lines, ok = rr.fetch_ci(c, info)
    assert not ok and "AssertionError" in lines[-1] and "hard-gating" in lines[2]


def test_github_request_comments_reviews_and_checks():
    t = rr.Target("github", "github.com", "o/r", "3")
    base = "https://api.github.com/repos/o/r"
    http = fake({
        f"{base}/pulls/3/comments": [{"id": 20, "user": {"login": "rev"}, "created_at": "2026-01-03", "body": "nit", "path": "x.py"}],
        f"{base}/pulls/3/reviews": [{"id": 30, "user": {"login": "rev"}, "submitted_at": "2026-01-04", "state": "CHANGES_REQUESTED", "body": "see comments"},
                                    {"id": 31, "user": {"login": "x"}, "submitted_at": "2026-01-05", "state": "COMMENTED", "body": ""}],
        f"{base}/pulls/3": {"title": "T", "state": "open", "merged_at": None, "user": {"login": "dev"},
                            "head": {"ref": "feat", "sha": "s1"}, "base": {"ref": "main"},
                            "html_url": "h", "draft": False, "body": None},
        f"{base}/issues/3/comments": [{"id": 10, "user": {"login": "pm"}, "created_at": "2026-01-02", "body": "ok"}],
        f"{base}/commits/s1/check-runs": {"check_runs": [
            {"name": "build", "conclusion": "failure", "html_url": "https://github.com/o/r/actions/runs/1/job/77", "app": {}}]},
        f"{base}/commits/s1/status": {"statuses": [{"context": "lint", "state": "success", "target_url": None}]},
        f"{base}/actions/jobs/77/logs": "step\nError: boom",
    })
    c = rr.Client(t, http=http)
    info = rr.fetch_request(c)
    assert info["description"] == "" and info["head_sha"] == "s1"
    kinds = [x["kind"] for x in rr.fetch_comments(c)]
    assert kinds == ["comment", "diff", "review"]          # empty COMMENTED review skipped
    lines, ok = rr.fetch_ci(c, info)
    assert not ok and lines[-1] == "Error: boom"


def test_bitbucket_cloud_pagination_and_statuses():
    t = rr.Target("bitbucket-cloud", "bitbucket.org", "ws/r", "9")
    base = "https://api.bitbucket.org/2.0/repositories/ws/r/pullrequests/9"
    http = fake({
        f"{base}/comments?pagelen=100": {"values": [{"id": 1, "user": {"display_name": "A"}, "created_on": "1",
                                                     "content": {"raw": "first"}}], "next": "https://next-page"},
        "https://next-page": {"values": [{"id": 2, "user": {"display_name": "B"}, "created_on": "2",
                                          "content": {"raw": "inline"}, "inline": {"path": "f.py"}},
                                         {"id": 3, "deleted": True, "created_on": "3"}]},
        f"{base}/statuses": {"values": [{"name": "pipeline", "state": "FAILED", "url": "u"}]},
        base: {"title": "T", "state": "OPEN", "author": {"display_name": "Dev"},
               "source": {"branch": {"name": "feat"}, "commit": {"hash": "h"}},
               "destination": {"branch": {"name": "main"}}, "links": {"html": {"href": "w"}}, "description": "D"},
    })
    c = rr.Client(t, http=http)
    info = rr.fetch_request(c)
    assert (info["state"], info["source"], info["target"]) == ("open", "feat", "main")
    comments = rr.fetch_comments(c)
    assert [x["id"] for x in comments] == [1, 2] and comments[1]["path"] == "f.py"
    lines, ok = rr.fetch_ci(c, info)
    assert not ok and "FAILED" in lines[0]


def test_bitbucket_server_activities_threads_and_build_status():
    t = rr.Target("bitbucket-server", "bb.corp", "CLMQ/pricing", "15")
    base = "https://bb.corp/rest/api/1.0/projects/CLMQ/repos/pricing/pull-requests/15"
    http = fake({
        f"{base}/activities": {"isLastPage": True, "values": [
            {"action": "APPROVED"},
            {"action": "COMMENTED", "commentAnchor": {"path": "p.py"},
             "comment": {"id": 1, "author": {"name": "rev"}, "createdDate": 100, "text": "why?",
                         "comments": [{"id": 2, "author": {"name": "dev"}, "createdDate": 200, "text": "because"}]}}]},
        base: {"title": "T", "state": "OPEN", "author": {"user": {"name": "dev"}},
               "fromRef": {"displayId": "feat", "latestCommit": "c1"}, "toRef": {"displayId": "develop"},
               "links": {"self": [{"href": "w"}]}, "description": ""},
        "https://bb.corp/rest/build-status/1.0/commits/c1": {"values": [{"key": "ci", "state": "SUCCESSFUL", "url": "u"}]},
    })
    c = rr.Client(t, http=http)
    info = rr.fetch_request(c)
    assert (info["source"], info["target"], info["url"]) == ("feat", "develop", "w")
    comments = rr.fetch_comments(c)
    assert [(x["id"], x["kind"]) for x in comments] == [(1, "diff"), (2, "diff")]
    lines, ok = rr.fetch_ci(c, info)
    assert ok and "SUCCESSFUL" in lines[0]


def test_script_is_read_only():
    """Only read subcommands exist, and curl is never told to use a write method."""
    src = SCRIPT.read_text(encoding="utf-8")
    for word in ("POST", "PUT", "PATCH", "DELETE", "request =", "data-binary"):
        assert word not in src, word
    with pytest.raises(SystemExit):
        rr.main(["comment", "1", "text"])
    with pytest.raises(SystemExit):
        rr.main(["set-description", "1", "text"])
