"""Private CLI bridge: byte-identical crawlers with their evidence root relocated."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('source',choices=('parliament','archive','anemi','wikimedia','other'))
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--timeout',type=float,default=1800)
    arguments=list(sys.argv[1:]);split=arguments.index('--')
    args=parser.parse_args(arguments[:split]);native=arguments[split+1:]
    root=args.evidence_root.resolve();root.mkdir(parents=True,exist_ok=True)
    originals=Path(__file__).resolve().parents[2]/'_vendor/source_clis/scripts/fetch'
    with tempfile.TemporaryDirectory(prefix='greekocr-crawl-') as temporary:
        stage=Path(temporary)
        shutil.copytree(originals,stage/'scripts/fetch')
        (stage/'docs/evidence').mkdir(parents=True)
        (stage/'docs/evidence/o4c').symlink_to(root,target_is_directory=True)
        # A caller can stage the optional S17 exclusion manifest adjacent to O4c.
        if (root.parent/'s17').is_dir():
            (stage/'docs/evidence/s17').symlink_to(root.parent/'s17',target_is_directory=True)
        result=subprocess.run([sys.executable,str(stage/f'scripts/fetch/o4c_discover_{args.source}.py'),*native],
                              timeout=args.timeout)
        return result.returncode

if __name__=='__main__':raise SystemExit(main())
