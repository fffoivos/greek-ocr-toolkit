"""Read-only CODE_SHA component audit; exit 1 means the brief requires STOP."""
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[3]
CODE_SHA = '3b4090bf9b15d2d2cac53ee55161e936157ec0e5'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def blob(path, revision=CODE_SHA):
    return git('show', revision + ':' + path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    resolved = git('rev-parse', CODE_SHA + '^{commit}').decode().strip()
    report_path = 'docs/records/harvest/seg_steps/s5_adopt/REPORT.md'
    last_line = blob(report_path).decode().rstrip().splitlines()[-1]
    pipe032_report_path = 'docs/records/harvest/pipe032/REPORT.md'
    pipe032_last_line = blob(pipe032_report_path).decode().rstrip().splitlines()[-1]
    assert last_line.startswith('SEG10 READY'), 'required SEG10 READY gate failed'
    assert pipe032_last_line.startswith('PIPE032 READY'), 'required PIPE032 READY gate failed'
    versions_path = 'docs/harvest/line_pipeline/tool_versions.json'
    manifest = json.loads(blob(versions_path))
    expected_versions = dict(segmentation='0.13', content_gate='0.3', final_eligibility='0.3', composer='0.3', census='0.7', numerics='0.3', polytonic='0.7', cyrillic='0.3')
    for name, version in expected_versions.items():
        assert manifest['tools'][name]['version'] == version, (name, version)
    assert manifest['tools']['segmentation']['label'] == '0.9-s5'
    assert 'PIPELINE_VERSION = \"0.3.2\"' in blob('greekocr/harvest/line_pipeline.py').decode()
    components, stages = [], []
    for name, tool in manifest['tools'].items():
        actual_components = {}
        for component, expected in tool['components'].items():
            project, relative = component.split('/', 1)
            source = relative if project in ('greek-ocr-toolkit-main-next', 'greek-ocr-toolkit-pipe032') else (
                'docs/harvest/seg_census/package/projects/' + component)
            data = blob(source)
            actual = sha(data)
            actual_components[component] = actual
            tree = git('ls-tree', CODE_SHA, '--', source).decode().strip()
            oid = tree.split()[2]
            object_bytes = git('cat-file', 'blob', oid)
            assert object_bytes == data
            components.append(dict(tool=name, component=component, source_path=source,
                bytes=len(data), git_blob=oid, git_ls_tree=tree,
                expected_sha256=expected, actual_sha256=actual, match=actual == expected))
        encode = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
        assert sha(encode(tool['components'])) == tool['digest']
        actual_digest = sha(encode(actual_components))
        stages.append(dict(tool=name, version=tool['version'], recorded_digest=tool['digest'],
            actual_digest=actual_digest, match=actual_digest == tool['digest']))
    runtime = []
    for source in git('ls-tree', '-r', '--name-only', CODE_SHA,
                      'scripts/harvest/filter_runtime/').decode().splitlines():
        current, lineage = blob(source), blob(source, '3679c8412')
        runtime.append(dict(path=source, code_sha256=sha(current),
                            lineage_sha256=sha(lineage), match=current == lineage))
    mismatches = [v for v in components if not v['match']]
    result = dict(status='STOPPED' if mismatches else 'COMPONENT_AUDIT_PASS',
        code_sha=resolved, project_prefix_map={'greek-ocr-toolkit-pipe032': 'CODE_SHA repository root', 'greek-ocr-toolkit-main-next': 'CODE_SHA repository root (legacy alias)'},
        pipeline_version='0.3.2', expected_versions=expected_versions, segmentation_label='0.9-s5',
        pipe032_report_path=pipe032_report_path, pipe032_last_line=pipe032_last_line, pipe032_ready=True,
        seg10_report_path=report_path, seg10_last_line=last_line,
        seg10_ready=last_line.startswith('SEG10 READY'), versions_path=versions_path,
        versions_sha256=sha(blob(versions_path)), components=components,
        component_checks=len(components), component_mismatches=mismatches, stages=stages,
        runtime_lineage_commit=git('rev-parse', '3679c8412^{commit}').decode().strip(),
        runtime_source_comparison=runtime,
        runtime_binary_manifest_verification='NOT COMPLETED: source lineage checked; binary runtime manifest not audited')
    print(json.dumps(result, indent=2))
    return 1 if mismatches else 0


if __name__ == '__main__':
    raise SystemExit(main())
