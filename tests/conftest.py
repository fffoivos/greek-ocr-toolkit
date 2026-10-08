"""All tests are offline, CPU-only, with no source checkouts required."""
import json
import os
from pathlib import Path
import socket
import urllib.request
import pytest

os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', GIT_OPTIONAL_LOCKS='0',
                  CUDA_VISIBLE_DEVICES='', TOKENIZERS_PARALLELISM='false')

@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError('test attempted live network')
    monkeypatch.setattr(socket.socket, 'connect', blocked)
    monkeypatch.setattr(socket.socket, 'connect_ex', blocked)
    monkeypatch.setattr(urllib.request, 'urlopen', blocked)

@pytest.fixture(scope='session', autouse=True)
def cpu_threads():
    import torch
    torch.set_num_threads(2)

@pytest.fixture
def partition_file(tmp_path):
    path = tmp_path/'partition.json'
    path.write_text(json.dumps(dict(schema='o4b-documents-v1',reviewed=True,
        documents={'book':'work','mirror':'work','held':'excluded','c1':'c1work'},
        cohorts={'O5_E1_test':dict(documents=['held'],evidence='recorded test fixture'),
                 'C1':dict(documents=['c1'],evidence='recorded test fixture')},
        split_overrides={'work':'train'})))
    return path

@pytest.fixture
def line_record(tmp_path):
    from PIL import Image
    crop = tmp_path/'line.png'; Image.new('L',(160,48),255).save(crop)
    return dict(line_id='line-1',text='ἅλφα βῆτα',crop_path=str(crop),admitted=True,
                source_doc_id='book',source_dataset='polyton_db',script_class='greek_poly',
                label_tier='gold',licence='CC-BY-4.0')
