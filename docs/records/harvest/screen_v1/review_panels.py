"""Create local pixel witnesses; these are review panels, never training recuts."""
from PIL import Image, ImageDraw, ImageFont
from screen import OUT, rows


def panel(batch, path, byid):
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 23)
    images = []
    for r in batch:
        f = byid[r['id']]
        with Image.open(f['crop_page_path']) as page:
            crop = page.crop(f['crop_bbox']).convert('RGB')
        scale = min(1.5, 1900/crop.width)
        crop = crop.resize((round(crop.width*scale), round(crop.height*scale)))
        images.append(crop)
    canvas = Image.new('RGB', (2000, sum(max(130, im.height+65) for im in images)+20), 'white')
    draw = ImageDraw.Draw(canvas)
    y = 10
    for r, im in zip(batch, images):
        label = r['track']+'/'+r['source']+' '+r.get('card_id', r['id'])
        draw.text((15, y), label, font=font, fill='black')
        canvas.paste(im, (20, y+40))
        y += max(130, im.height+65)
    canvas.save(path)


def run():
    features = rows(OUT/'features.jsonl')
    byid = {r['id']: r for r in features}
    changed = [c for c in rows(OUT/'card_eval.jsonl') if c['assembly_changed']]
    for path in (OUT/'receipts').glob('changed_cards_*.png'):
        path.unlink()
    for i in range(0, len(changed), 6):
        panel(changed[i:i+6], OUT/'receipts'/f'changed_cards_{i//6+1:02d}.png', byid)
    samples = rows(OUT/'receipts/random_changed_non_cards.jsonl')
    for i in range(0, len(samples), 5):
        panel(samples[i:i+5], OUT/'receipts'/f'random_changed_{i//5+1:02d}.png', byid)
    controls = [c for c in rows(OUT/'card_eval.jsonl') if
                (c['track'], c['source'], c['card_id']) in {
                    ('ia', 'poly1850', 'c032'), ('intl', 'bsb', 'c020'), ('gr', 'pleias', 'c021')}]
    date = next(r for r in features if r['id']=='elstat--GRESYE_01_0001_00164-fbc4a190--000021-l0015')
    panel(controls+[date], OUT/'receipts/negative_controls.png', byid)
    print('review panels', len(changed), 'changed cards;', len(samples), 'random non-cards; four controls')


if __name__ == '__main__':
    run()
