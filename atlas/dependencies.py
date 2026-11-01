import json
import re

MANIFESTS = ("requirements.txt", "pyproject.toml", "package.json", "Cargo.toml", "go.mod")

def parse_requirements(text):
    result = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(("-", "--")):
            continue
        name = re.split(r"[<=>!~;\[]", line, maxsplit=1)[0].strip()
        if name:
            result.append(name)
    return result

def parse_package_json(text):
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return []
    names = set()
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        names.update((data.get(section) or {}).keys())
    return sorted(names)

def parse_pyproject(text):
    # Lightweight parser for common PEP 621 and Poetry dependency declarations.
    deps = []
    in_dependencies = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("["):
            in_dependencies = line in ("[project]", "[tool.poetry.dependencies]", "[tool.poetry.group.dev.dependencies]")
        elif in_dependencies and line.startswith(("dependencies", "optional-dependencies")):
            continue
        elif in_dependencies and "=" in line:
            name = line.split("=", 1)[0].strip().strip('"').strip("'")
            if name and name not in ("python", "dev"):
                deps.append(name)
    return sorted(set(deps))

def parse_go_mod(text):
    deps = []
    in_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("require ("):
            in_block = True
            continue
        if in_block and line == ")":
            in_block = False
            continue
        if line.startswith("require ") or in_block:
            parts = line.replace("require ", "", 1).split()
            if parts and not parts[0].startswith("//"):
                deps.append(parts[0])
    return sorted(set(deps))

def parse_manifest(path, text):
    if path == "requirements.txt":
        return parse_requirements(text)
    if path == "package.json":
        return parse_package_json(text)
    if path == "pyproject.toml":
        return parse_pyproject(text)
    if path == "go.mod":
        return parse_go_mod(text)
    if path == "Cargo.toml":
        # Extract common simple `name = "version"` entries.
        return sorted(set(re.findall(r'^([A-Za-z0-9_-]+)\s*=\s*["\\']', text, re.M)))
    return []

def fetch_manifest_dependencies(client, full_name, branch):
    found = []
    for path in MANIFESTS:
        try:
            content = client.get_file_text(full_name, path, branch)
        except Exception:
            continue
        for dep in parse_manifest(path, content):
            found.append((path, dep))
    return found
