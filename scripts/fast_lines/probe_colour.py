"""Check development-image modes/channels; all 54 were grayscale in Q6."""
from collections import Counter
import json
from pathlib import Path
from PIL import Image, ImageChops


def main():
    paths = sorted(Path('.astra/pages').glob('*.png'))
    assert len(paths) == 54
    rows = []
    for path in paths:
        with Image.open(path) as source:
            mode = source.mode
            r, g, b = source.convert('RGB').split()
            difference = max(ImageChops.difference(a, z).getextrema()[1]
                             for a, z in ((r, g), (g, b), (r, b)))
            rows.append({'page': path.stem, 'mode': mode,
                         'max_channel_difference': difference})
    out = Path('.astra/fast_lines/out/q6_review')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'colour_probe.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(Counter((r['mode'], r['max_channel_difference']) for r in rows))
    print('non-grey:', [r['page'] for r in rows if r['max_channel_difference']])


if __name__ == '__main__':
    main()
