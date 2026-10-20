"""Offline S8a3 payload acceptance, bound to the exact extraction request."""
from greekocr.ops.data_root import input_path as _data_input
import gzip
import hashlib
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/records/labelfix/spellcheck/S8_DEV/evidence'
EXPECTED = 'fae3140ea1e789ca817d3eec3ec71ae5d47774cf43503b9fa0b25aa54d64e4a2'


def sha(path):
    return hashlib.sha256(_data_input(path).read_bytes()).hexdigest()


def verify():
    request = json.loads((E / 'S8a3/request.json').read_text())
    receipt = json.loads((E / 'S8a3/remote_receipt.json').read_text())
    config = json.loads((E / 'S8a3/job_config.json').read_text())
    remote = json.loads(gzip.decompress((_data_input(E / 'remote.json.gz')).read_bytes()))
    local = json.loads(gzip.decompress((_data_input(E / 'dev_c1_alignments.json.gz')).read_bytes()))
    fingerprint = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    assert fingerprint == receipt['request_sha256'] == config['request_sha256'] == remote['request_sha256']
    assert sha(E / 'remote.json.gz') == receipt['remote_sha256'] == EXPECTED
    assert receipt['complete'] and receipt['error'] is None and remote['complete']
    assert receipt['slurm_job_id'] == '3680506'
    assert receipt['inference_runs'] == remote['inference_runs'] == receipt['input_writes'] == 0
    ids = (E.parent / 'S8_DEV_ids.txt').read_text().split()
    assert len(ids) == len(set(ids)) == len(request['ids']) == config['expected_ids'] == 600
    wanted = set(ids)
    assert wanted == set(request['ids']) == set(remote['ids']) == set(remote['runtime']) == set(remote['alignments'])
    assert len(request['crop_to_id']) == 600 and set(request['crop_to_id'].values()) == wanted
    missing = set(request['missing_alignment_ids'])
    assert len(missing) == len(request['missing_alignment_ids']) == receipt['final']['alignments'] == 166
    assert set(local) == wanted - missing and len(local) == 434
    assert sha(E / 'dev_c1_alignments.json.gz') == receipt['local_alignment_sha256'] == remote['local_alignment_custody']['sha256']
    assert all(remote['alignments'][k] == row for k, row in local.items())
    assert receipt['final']['merged_alignments'] == receipt['final']['runtime'] == 600
    for field in ('missing_runtime_ids', 'missing_A_ids', 'missing_alignment_ids'):
        assert remote[field] == []
    assert len(remote['BE_done']) == len(set(remote['BE_done'])) == receipt['final']['BE'] == config['expected_BE_shards'] == 974
    shards = {row['BE_shard'] for row in remote['runtime'].values()}
    assert shards <= set(remote['BE_done'])
    assert shards == set(remote['A_done']) and len(shards) == receipt['final']['A'] == 418
    assert len(remote['alignment_done']) == receipt['final']['alignment'] == 4
    for key in ids:
        row, alignment = remote['runtime'][key], remote['alignments'][key]
        assert row['id'] == key and row['historical_A_verified']
        assert 'detector' not in row and 'modes' not in row
        text = unicodedata.normalize('NFD', row['recogniser_text'])
        assert text == row['recogniser_nfd'] == alignment['alignment']['prediction']
        crop = 'docs/harvest/' + alignment['crop'].split('docs/harvest/', 1)[1]
        assert request['crop_to_id'][crop] == key
        assert set(row['historical_field_sha256']) == {'recogniser_text', 'recogniser_nfd', 'coverage', 'r1_predictions'}
        for field, expected in row['historical_field_sha256'].items():
            actual = hashlib.sha256(json.dumps(row[field], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            assert actual == expected, (key, field)
        assert set(row['peer_predictions']) == set(row['peer_coverage']) == {'B', 'E'}
        for predictions, coverage in [(row['r1_predictions'], row['coverage'])] + [
                (row['peer_predictions'][arm], row['peer_coverage'][arm]) for arm in ('B', 'E')]:
            starts = [p['start'] for p in predictions]
            assert len(starts) == len(set(starts))
            assert set(starts) == {c['start'] for c in coverage if c['scored']}, key
            assert all(0 <= start < len(text) for start in starts)
    result = dict(status='PASS', schema='s8a4-evidence-acceptance-v1',
                  remote_sha256=EXPECTED, request_sha256=fingerprint,
                  request_file='S8a3/request.json', receipt_file='S8a3/remote_receipt.json',
                  receipt_sha256=sha(E / 'S8a3/remote_receipt.json'),
                  runtime=600, historical_A_verified=600, alignment_reader_crop_joins=600,
                  remote_alignments=166, local_alignments=434, local_records_identical=True,
                  BE_shards=974, A_shards=418, alignment_shards=4,
                  inference_runs=0, network=False, input_writes=0,
                  custody_limit=receipt['custody_limit'])
    (E / 'S8a4_evidence_acceptance.json').write_text(json.dumps(result, indent=2) + '\n')
    return remote


def main():
    verify()
    stop = E / 'extraction_stop.json'
    archive = E / 'extraction_stop_superseded_S8a3.json'
    old = json.loads(stop.read_text())
    if old.get('status') == 'STOP':
        assert not archive.exists(), 'do not overwrite archived STOP'
        stop.rename(archive)
    else:
        assert old.get('status') == 'SUPERSEDED' and archive.exists()
    note = dict(status='SUPERSEDED', superseded_by='S8a3 job 3680506; accepted locally in S8a4',
                previous_marker=archive.name, previous_sha256=sha(archive),
                receipt='S8a3/remote_receipt.json', receipt_sha256=sha(E / 'S8a3/remote_receipt.json'),
                acceptance='S8a4_evidence_acceptance.json', complete=True,
                note='All requested saved evidence is local and verified. Preparation is authorized offline; no further network access.')
    stop.write_text(json.dumps(note, indent=2) + '\n')
    print('PASS: request-bound 600 runtimes/alignments; 166 fetched + 434 unchanged local; STOP superseded.')


if __name__ == '__main__':
    main()
