#!/usr/bin/env python3
"""Read a merge request / pull request from GitLab, GitHub or Bitbucket. Read-only.

The provider is detected automatically from the reference URL, or from the
`origin` remote when you pass a bare number:

  github.com, GitHub Enterprise hosts      -> GitHub        (token: GITHUB_TOKEN or GH_TOKEN)
  gitlab.com, self-managed GitLab hosts    -> GitLab        (token: GITLAB_TOKEN)
  bitbucket.org                            -> Bitbucket Cloud
        (token: BITBUCKET_TOKEN, or BITBUCKET_USERNAME + BITBUCKET_APP_PASSWORD)
  Bitbucket Server / Data Center hosts     -> Bitbucket Server (token: BITBUCKET_TOKEN)

Hosts whose name doesn't reveal the provider can be mapped with
GODMODE_GIT_PROVIDERS="git.corp.example=gitlab,code.corp.example=bitbucket-server"
or overridden per call with --provider.

Commands (all read-only):
  locate     <ref>   provider, host, project and number, as JSON
  show       <ref>   title, state, author, branches, URL, draft flag, description
  comments   <ref>   discussion and review comments, oldest first
  pipelines  <ref>   latest CI status, with log tails for failed required jobs where the API allows

HTTP goes through `curl` (not Python's ssl module): some corporate networks
sit behind a TLS-intercepting proxy whose CA Python rejects but curl accepts.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
from dataclasses import dataclass

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

PROVIDERS = ("gitlab", "github", "bitbucket-cloud", "bitbucket-server")


class ReviewError(Exception):
    pass


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


@dataclass
class Target:
    provider: str
    host: str
    project: str      # gitlab: group/sub/repo; github/bb-cloud: owner/repo; bb-server: PROJECTKEY/repo
    number: str

    @property
    def label(self):
        return f"!{self.number}" if self.provider == "gitlab" else f"#{self.number}"


# --------------------------------------------------------------------- detection
URL_PATTERNS = [
    ("gitlab", re.compile(r"^(?:https?://)?([^/]+)/(.+?)/-/merge_requests/(\d+)")),
    ("github", re.compile(r"^(?:https?://)?([^/]+)/([^/]+/[^/]+)/pull/(\d+)")),
    ("bitbucket-server", re.compile(r"^(?:https?://)?([^/]+)(?:/[^/]+)*?/projects/([^/]+)/repos/([^/]+)/pull-requests/(\d+)", re.I)),
    ("bitbucket-cloud", re.compile(r"^(?:https?://)?([^/]+)/([^/]+/[^/]+)/pull-requests/(\d+)")),
]


def provider_from_host(host, path_hint=""):
    host_l = host.lower()
    mapping = os.environ.get("GODMODE_GIT_PROVIDERS", "")
    for pair in filter(None, (p.strip() for p in mapping.split(","))):
        if "=" in pair:
            h, prov = (x.strip().lower() for x in pair.split("=", 1))
            if h == host_l:
                if prov == "bitbucket":
                    prov = "bitbucket-cloud" if host_l == "bitbucket.org" else "bitbucket-server"
                if prov not in PROVIDERS:
                    raise ReviewError(f"GODMODE_GIT_PROVIDERS maps {h} to unknown provider '{prov}'")
                return prov
    if host_l == "bitbucket.org":
        return "bitbucket-cloud"
    if "github" in host_l:
        return "github"
    if "gitlab" in host_l:
        return "gitlab"
    if "bitbucket" in host_l or "/scm/" in path_hint or re.search(r"/projects/[^/]+/repos/", path_hint, re.I):
        return "bitbucket-server"
    return None


def parse_remote(url):
    """Return (host, project_path, provider_guess) from a git remote URL."""
    url = url.strip()
    m = re.match(r"^ssh://(?:[^@/]+@)?([^/:]+)(?::\d+)?/(.+?)(?:\.git)?/?$", url)
    if not m:
        m = re.match(r"^(?:[^@/]+@)?([^/:]+):(.+?)(?:\.git)?/?$", url) if "://" not in url else None
    if not m:
        m = re.match(r"^https?://(?:[^@/]+@)?([^/]+)/(.+?)(?:\.git)?/?$", url)
    if not m:
        raise ReviewError(f"could not parse host/project out of remote url: {url}")
    host, path = m.group(1), m.group(2)
    provider = provider_from_host(host, "/" + path)
    if provider == "bitbucket-server":
        path = re.sub(r"^scm/", "", path, flags=re.I)
    return host, path, provider


def git_remote_url(remote="origin"):
    try:
        return subprocess.run(["git", "remote", "get-url", remote], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise ReviewError("could not read git remote 'origin' here: pass a full MR/PR URL, run inside "
                          "the checkout, or pass --project and --host")


def resolve(ref, provider=None, project=None, host=None, remote_url=None):
    for prov, rx in URL_PATTERNS:
        m = rx.match(ref)
        if not m:
            continue
        if prov == "bitbucket-server":
            h, key, slug, num = m.groups()
            return Target(provider or "bitbucket-server", h, f"{key}/{slug}", num)
        h, proj, num = m.groups()
        detected = provider or provider_from_host(h)
        if prov == "bitbucket-cloud" and detected not in (None, "bitbucket-cloud"):
            continue
        if prov == "github" and detected not in (None, "github"):
            continue
        return Target(detected or prov, h, proj, num)
    ref = ref.lstrip("!#")
    if not ref.isdigit():
        raise ReviewError(f"'{ref}' is not a merge/pull request URL or number")
    if project:
        h = host or {"github": "github.com", "gitlab": "gitlab.com", "bitbucket-cloud": "bitbucket.org"}.get(provider or "", "")
        prov = provider or (provider_from_host(h) if h else None)
        if not h or not prov:
            raise ReviewError("with --project, also pass --host (and --provider if the host name doesn't reveal it)")
        return Target(prov, h, project, ref)
    h, path, guess = parse_remote(remote_url or git_remote_url())
    prov = provider or guess
    if not prov:
        raise ReviewError(f"can't tell which provider {h} is: pass --provider "
                          f"({', '.join(PROVIDERS)}) or set GODMODE_GIT_PROVIDERS={h}=<provider>")
    return Target(prov, h, path, ref)


# --------------------------------------------------------------------- HTTP
def api_base(t):
    if t.provider == "gitlab":
        return f"https://{t.host}/api/v4"
    if t.provider == "github":
        return "https://api.github.com" if t.host.lower() == "github.com" else f"https://{t.host}/api/v3"
    if t.provider == "bitbucket-cloud":
        return "https://api.bitbucket.org/2.0"
    return f"https://{t.host}/rest/api/1.0"


def auth_headers(provider):
    if provider == "gitlab":
        token = os.environ.get("GITLAB_TOKEN")
        if token:
            return [f"PRIVATE-TOKEN: {token}"]
        raise ReviewError("GITLAB_TOKEN is not set (personal access token with read_api scope)")
    if provider == "github":
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            return [f"Authorization: Bearer {token}", "Accept: application/vnd.github+json",
                    "X-GitHub-Api-Version: 2022-11-28"]
        raise ReviewError("GITHUB_TOKEN (or GH_TOKEN) is not set (token with read access to pull requests)")
    token = os.environ.get("BITBUCKET_TOKEN")
    if token:
        return [f"Authorization: Bearer {token}"]
    user, pw = os.environ.get("BITBUCKET_USERNAME"), os.environ.get("BITBUCKET_APP_PASSWORD")
    if provider == "bitbucket-cloud" and user and pw:
        return ["Authorization: Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()]
    raise ReviewError("BITBUCKET_TOKEN is not set" + (
        " (or BITBUCKET_USERNAME + BITBUCKET_APP_PASSWORD)" if provider == "bitbucket-cloud" else
        " (HTTP access token with project/repository read)"))


def curl_get(url, headers, raw=False):
    """GET via curl. The config goes to curl on stdin so tokens never appear in the process list."""
    lines = [f'url = "{url}"', "silent", "show-error", "location", 'write-out = "\\n%{http_code}"', "ssl-no-revoke"]
    lines += [f'header = "{h}"' for h in headers]
    proc = subprocess.run(["curl", "-K", "-"], input="\n".join(lines) + "\n",
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise ReviewError(f"curl failed calling {url}: {proc.stderr.strip()}")
    content, _, code = proc.stdout.rpartition("\n")
    if not code.isdigit():
        raise ReviewError(f"unexpected curl output calling {url}: {proc.stdout[:300]}")
    if int(code) >= 400:
        raise ReviewError(f"HTTP {code} from {url}: {content[:400]}")
    if raw:
        return content
    return json.loads(content) if content.strip() else None


class Client:
    def __init__(self, target, http=curl_get):
        self.t, self.http = target, http
        self.base = api_base(target)
        self.headers = auth_headers(target.provider)

    def get(self, path, raw=False):
        url = path if path.startswith("http") else self.base + path
        return self.http(url, self.headers, raw)

    def paged(self, path):
        """Follow each provider's pagination and return all items."""
        items, url = [], path
        while url:
            data = self.get(url)
            if self.t.provider == "bitbucket-cloud":
                items += data.get("values", [])
                url = data.get("next")
            elif self.t.provider == "bitbucket-server":
                items += data.get("values", [])
                url = None if data.get("isLastPage", True) else \
                    f"{path}{'&' if '?' in path else '?'}start={data.get('nextPageStart')}"
            else:
                items += data or []
                url = None if not data or len(data) < 100 else _next_page(url)
        return items


def _next_page(url):
    m = re.search(r"([?&]page=)(\d+)", url)
    if m:
        return url[:m.start(2)] + str(int(m.group(2)) + 1) + url[m.end(2):]
    return url + ("&" if "?" in url else "?") + "page=2"


# --------------------------------------------------------------------- normalisation
def enc(project):
    return urllib.parse.quote(project, safe="")


def bb_server_paths(project):
    key, slug = project.split("/", 1)
    return f"/projects/{key}/repos/{slug}"


def fetch_request(c):
    t = c.t
    if t.provider == "gitlab":
        mr = c.get(f"/projects/{enc(t.project)}/merge_requests/{t.number}")
        return dict(title=mr["title"], state=mr["state"], author=mr["author"]["username"],
                    source=mr["source_branch"], target=mr["target_branch"], url=mr["web_url"],
                    draft=bool(mr.get("draft") or mr.get("work_in_progress")),
                    description=mr.get("description") or "", head_sha=mr.get("sha"))
    if t.provider == "github":
        pr = c.get(f"/repos/{t.project}/pulls/{t.number}")
        state = "merged" if pr.get("merged_at") else pr["state"]
        return dict(title=pr["title"], state=state, author=pr["user"]["login"],
                    source=pr["head"]["ref"], target=pr["base"]["ref"], url=pr["html_url"],
                    draft=bool(pr.get("draft")), description=pr.get("body") or "",
                    head_sha=pr["head"]["sha"])
    if t.provider == "bitbucket-cloud":
        pr = c.get(f"/repositories/{t.project}/pullrequests/{t.number}")
        return dict(title=pr["title"], state=pr["state"].lower(),
                    author=(pr.get("author") or {}).get("display_name", "?"),
                    source=pr["source"]["branch"]["name"], target=pr["destination"]["branch"]["name"],
                    url=pr["links"]["html"]["href"], draft=bool(pr.get("draft")),
                    description=pr.get("description") or "",
                    head_sha=(pr["source"].get("commit") or {}).get("hash"))
    pr = c.get(f"{bb_server_paths(t.project)}/pull-requests/{t.number}")
    url = ((pr.get("links") or {}).get("self") or [{}])[0].get("href", "")
    return dict(title=pr["title"], state=pr["state"].lower(),
                author=pr["author"]["user"].get("name", "?"),
                source=pr["fromRef"]["displayId"], target=pr["toRef"]["displayId"], url=url,
                draft=bool(pr.get("draft")), description=pr.get("description") or "",
                head_sha=pr["fromRef"].get("latestCommit"))


def fetch_comments(c):
    """Return [{id, author, created, body, kind, path}] oldest first."""
    t, out = c.t, []
    if t.provider == "gitlab":
        for n in c.paged(f"/projects/{enc(t.project)}/merge_requests/{t.number}/notes?per_page=100&sort=asc&order_by=created_at&page=1"):
            pos = n.get("position") or {}
            out.append(dict(id=n["id"], author=n["author"]["username"], created=n["created_at"], body=n["body"],
                            kind="system" if n.get("system") else ("diff" if pos else "comment"),
                            path=pos.get("new_path")))
    elif t.provider == "github":
        for n in c.paged(f"/repos/{t.project}/issues/{t.number}/comments?per_page=100&page=1"):
            out.append(dict(id=n["id"], author=n["user"]["login"], created=n["created_at"], body=n["body"] or "",
                            kind="comment", path=None))
        for n in c.paged(f"/repos/{t.project}/pulls/{t.number}/comments?per_page=100&page=1"):
            out.append(dict(id=n["id"], author=n["user"]["login"], created=n["created_at"], body=n["body"] or "",
                            kind="diff", path=n.get("path")))
        for r in c.paged(f"/repos/{t.project}/pulls/{t.number}/reviews?per_page=100&page=1"):
            if (r.get("body") or "").strip() or r.get("state") in ("CHANGES_REQUESTED", "APPROVED"):
                out.append(dict(id=r["id"], author=r["user"]["login"], created=r.get("submitted_at") or "",
                                body=f"[review: {r.get('state')}] {r.get('body') or ''}".strip(), kind="review", path=None))
    elif t.provider == "bitbucket-cloud":
        for n in c.paged(f"/repositories/{t.project}/pullrequests/{t.number}/comments?pagelen=100"):
            if n.get("deleted"):
                continue
            inline = n.get("inline") or {}
            out.append(dict(id=n["id"], author=(n.get("user") or {}).get("display_name", "?"), created=n["created_on"],
                            body=(n.get("content") or {}).get("raw", ""), kind="diff" if inline else "comment",
                            path=inline.get("path")))
    else:
        for a in c.paged(f"{bb_server_paths(t.project)}/pull-requests/{t.number}/activities?limit=100"):
            cm = a.get("comment")
            if a.get("action") != "COMMENTED" or not cm:
                continue
            anchor = a.get("commentAnchor") or {}
            stack = [cm]
            while stack:
                x = stack.pop(0)
                out.append(dict(id=x["id"], author=x["author"].get("name", "?"), created=str(x.get("createdDate", "")),
                                body=x.get("text", ""), kind="diff" if anchor else "comment", path=anchor.get("path")))
                stack += x.get("comments") or []
    return sorted(out, key=lambda x: str(x["created"]))


def fetch_ci(c, info):
    """Return (lines, ok): human-readable CI summary."""
    t, lines = c.t, []
    if t.provider == "gitlab":
        pipes = c.get(f"/projects/{enc(t.project)}/merge_requests/{t.number}/pipelines") or []
        if not pipes:
            return ["(no pipelines found for this MR)"], True
        p = max(pipes, key=lambda x: x["id"])
        lines += [f"pipeline #{p['id']} status: {p['status']}  sha: {p['sha'][:8]}", f"url: {p['web_url']}"]
        if p["status"] in ("failed", "canceled"):
            jobs = c.get(f"/projects/{enc(t.project)}/pipelines/{p['id']}/jobs?per_page=100") or []
            gating = [j for j in jobs if j["status"] == "failed" and not j.get("allow_failure")]
            lines.append("hard-gating job failures (allow_failure: false):" if gating else
                         "no hard-gating job failures (failed jobs all have allow_failure: true)")
            for j in gating:
                trace = c.get(f"/projects/{enc(t.project)}/jobs/{j['id']}/trace", raw=True) or ""
                lines += [f"--- job #{j['id']} {j['name']} (trace tail) ---", *trace.strip().splitlines()[-40:]]
        return lines, p["status"] not in ("failed", "canceled")
    sha = info.get("head_sha")
    if not sha:
        return ["(head commit unknown: cannot look up CI status)"], True
    if t.provider == "github":
        runs = (c.get(f"/repos/{t.project}/commits/{sha}/check-runs?per_page=100") or {}).get("check_runs", [])
        statuses = (c.get(f"/repos/{t.project}/commits/{sha}/status") or {}).get("statuses", [])
        if not runs and not statuses:
            return ["(no checks or statuses reported for the head commit)"], True
        failed_runs, failed_statuses = [], []
        for r in runs:
            verdict = r.get("conclusion") or r.get("status")
            lines.append(f"check {r['name']}: {verdict}  {r.get('html_url', '')}")
            if verdict in ("failure", "timed_out", "cancelled", "action_required"):
                failed_runs.append(r)
        for s in statuses:
            lines.append(f"status {s['context']}: {s['state']}  {s.get('target_url') or ''}")
            if s["state"] in ("failure", "error"):
                failed_statuses.append(s)
        bad = failed_runs + failed_statuses
        for r in failed_runs:
            # GitHub Actions jobs expose their log; other check providers only link out.
            m = re.search(r"/job/(\d+)", (r.get("html_url") or "") + " " + (r.get("details_url") or ""))
            if m:
                try:
                    log = c.get(f"/repos/{t.project}/actions/jobs/{m.group(1)}/logs", raw=True) or ""
                    lines += [f"--- {r['name']} (log tail) ---", *log.strip().splitlines()[-40:]]
                except ReviewError as e:
                    lines.append(f"--- {r['name']}: log unavailable ({e}) ---")
        return lines, not bad
    if t.provider == "bitbucket-cloud":
        statuses = c.paged(f"/repositories/{t.project}/pullrequests/{t.number}/statuses?pagelen=100")
    else:
        statuses = c.get(f"https://{t.host}/rest/build-status/1.0/commits/{sha}").get("values", [])
    if not statuses:
        return ["(no build statuses reported for this pull request)"], True
    bad = False
    for s in statuses:
        state = s.get("state", "?")
        lines.append(f"build {s.get('name') or s.get('key')}: {state}  {s.get('url', '')}")
        bad |= state in ("FAILED", "STOPPED")
    lines.append("(open failed builds at their URL for logs: the Bitbucket statuses API doesn't return them)")
    return lines, not bad


# --------------------------------------------------------------------- commands
def cmd_locate(t, args):
    print(json.dumps(dict(provider=t.provider, host=t.host, project=t.project, number=t.number,
                          label=t.label, api=api_base(t)), indent=2))


def cmd_show(t, args):
    info = fetch_request(Client(t))
    print(f"{t.label} {info['title']}")
    print(f"provider: {t.provider}  state: {info['state']}{'  [DRAFT]' if info['draft'] else ''}  "
          f"author: {info['author']}  {info['source']} -> {info['target']}")
    print(f"url: {info['url']}")
    print()
    print(info["description"] or "(no description)")


def cmd_comments(t, args):
    rows = fetch_comments(Client(t))
    if not rows:
        print("(no comments)")
    for r in rows:
        where = f" on {r['path']}" if r.get("path") else ""
        print(f"--- {r['id']} {r['author']} @ {r['created']} [{r['kind']}]{where} ---")
        print(r["body"])
        print()


def cmd_pipelines(t, args):
    c = Client(t)
    lines, _ = fetch_ci(c, fetch_request(c))
    print("\n".join(lines))


def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--provider", choices=PROVIDERS, help="override provider detection")
    common.add_argument("--project", help="project path (group/repo, owner/repo, or KEY/repo) instead of the git remote")
    common.add_argument("--host", help="host for --project (defaults per provider)")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                parents=[common])
    sub = p.add_subparsers(dest="action", required=True)
    for name, fn, help_ in [("locate", cmd_locate, "print detected provider/host/project/number"),
                            ("show", cmd_show, "print title/state/branches/description"),
                            ("comments", cmd_comments, "print discussion and review comments"),
                            ("pipelines", cmd_pipelines, "print latest CI status")]:
        s = sub.add_parser(name, help=help_, parents=[common])
        s.add_argument("ref", help="MR/PR URL, or a bare number (resolved via the origin remote)")
        s.set_defaults(func=fn)
    args = p.parse_args(argv)
    try:
        target = resolve(args.ref, args.provider, args.project, args.host)
        args.func(target, args)
    except ReviewError as e:
        fail(str(e))


if __name__ == "__main__":
    main()
