"""Write tests/agent-eval/devin-test-config.json: your Devin config plus pre-approved eval commands.

Your own config file is never changed. The generated file is git-ignored.
"""
import json
import os
import pathlib
import platform

here = pathlib.Path(__file__).resolve().parent
home = pathlib.Path(os.environ.get("APPDATA", "")) / "devin" if platform.system() == "Windows" \
    else pathlib.Path.home() / ".config" / "devin"
src = home / "config.json"
cfg = json.loads(src.read_text(encoding="utf-8")) if src.exists() else {}
allow = cfg.setdefault("permissions", {}).setdefault("allow", [])
# Only the run folders, never this folder: the generated config sits here and can hold credentials.
runs = here / "runs"
for entry in [f"Write({runs})", f"Read({runs})", "Exec(git)", "Exec(ls)", "Exec(cat)", "Exec(uv)",
              "Exec(python)", "Exec(pytest)", "Exec(node)", "Exec(Get-ChildItem)", "Exec(Where-Object)",
              "Exec(Select-Object)", "Exec(Get-Content)", "Exec(Test-Path)", "Exec(Set-Location)",
              "Exec(New-Item)", "Exec(Write-Output)", "Exec(Measure-Object)", "Exec(Select-String)",
              "Exec(Sort-Object)", "Exec(ForEach-Object)", "Exec(Get-Item)", "Exec(Out-String)",
              "Exec(Add-Content)", "Exec(Set-Content)", "Exec(Out-File)"]:
    if entry not in allow:
        allow.append(entry)
(here / "devin-test-config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
print("wrote devin-test-config.json")
