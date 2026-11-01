from atlas.dependencies import (
    parse_requirements, parse_package_json, parse_go_mod, parse_manifest
)

def test_parse_requirements_ignores_comments_and_options():
    assert parse_requirements("# comment\nrequests>=2\n-r other.txt\npandas") == ["requests", "pandas"]

def test_parse_package_json_collects_dependency_sections():
    text = '{"dependencies":{"react":"^18"},"devDependencies":{"vite":"*"}}'
    assert parse_package_json(text) == ["react", "vite"]

def test_parse_go_mod():
    text = "module example.com/x\nrequire (\n github.com/a/b v1.0.0\n)"
    assert parse_go_mod(text) == ["github.com/a/b"]

def test_parse_manifest_unknown_file():
    assert parse_manifest("unknown.txt", "x") == []
