"""Persist the actual unblinded pair and native-witness inspection."""
from pathlib import Path
import json,sys
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT));import run as current
prior=current.prior


def main():
    records=prior.rows(OUT/'dev/records.jsonl');review=[]
    # All 32 sheets / 160 pairs were inspected; all 14 component-loss witnesses
    # and five larger native contexts were then inspected. These annotations
    # describe that inspection, not an automatic metric or a blind verdict.
    confirmed_own={('ia_greek_latin','c019'):'Upper serif/tip of the target Latin f is shortened.',
                   ('ia_greek_latin','c023'):'Target initial gamma descender is cut flat at its lower end.',
                   ('ia_greek_latin','c040'):'Target capital E loses its upper-left serif.'}
    for r in records:
        source,card=r['stratum'],r['dev']['card_id'];overrun='crop_overrun' in r['dev']['errors']
        removed=overrun and (source,card)!=('gazette_modern','c015')
        note=[]
        if overrun:
            note.append('At least one previously readable neighbour fragment loses its substantial ink.' if removed else
                        'Readable E.S.Y.E. fragment below remains; only specks change; cached foreign pixels were already zero.')
        if (source,card)==('gazette_modern','c005'):
            note.append('Upper neighbour fragments removed, but readable lower neighbour fragment persists.')
        if source in ('lekythos_poly1900','kosmopolis_poly1900') and overrun:
            note.append('Faint outlines/halo remain at the former neighbour positions. Fragment-removal flag is not complete cleanup.')
        if (source,card)==('lekythos_poly1900','c024'):
            note.append('Own drop-cap H lower portion is cut; cached own pixels fail to account for that stroke.')
        if (source,card)==('lekythos_poly1900','c037'):
            note.append('Original right-edge clipping after E persists; no horizontal repair.')
        own_confirmed=None
        if r['dev']['crop_ok']=='y':
            if (source,card) in confirmed_own:
                own_confirmed=True;note.append(confirmed_own[(source,card)])
            elif r['own_pixels_lost']:
                note.append('Cached own-component loss verified natively; semantic attachment of the small removed piece remains unresolved.')
            else:
                own_confirmed=False;note.append('No new own body/accent/descender/apostrophe cutoff seen in the inspected pair.')
        if (source,card)==('ia_greek_latin','c001'):
            note.append('Larger native context confirms the iota subscript of toi is retained; the extra dot below is erased.')
        review.append(dict(id=r['id'],source=source,card_id=card,original_crop_ok=r['dev']['crop_ok'],
            changed=r['changed'],inspected=True,inspection='unblinded agent; every pair in 32 sheets; all 14 cached-loss components inspected natively',
            sheet=f'dev/review/{source}/sheet{(int(card[1:])-1)//5+1:02d}.png',
            original_overrun=overrun,readable_neighbour_fragment_removed=bool(removed) if overrun else None,
            complete_neighbour_cleanup_claimed=False,
            own_component_pixels_lost=r['own_pixels_lost'],target_own_ink_loss_confirmed=own_confirmed,
            note=' '.join(note)))
    prior.write_rows(OUT/'dev/visual_review.jsonl',review)
    summary={}
    for source in (*prior.SOURCES,'overall'):
        rr=[r for r in review if source=='overall' or r['source']==source]
        n=[r for r in rr if r['original_overrun']];y=[r for r in rr if r['original_crop_ok']=='y']
        removed=sum(r['readable_neighbour_fragment_removed'] for r in n)
        summary[source]=dict(inspected_pairs=len(rr),inspected_changed_y=sum(r['changed'] for r in y),
            overrun_cards=len(n),readable_neighbour_fragment_removed_cards=removed,
            readable_neighbour_fragment_removed_percent=100*removed/len(n),
            target_own_loss_visually_confirmed_y_cards=sum(r['target_own_ink_loss_confirmed'] is True for r in y))
    prior.write_json(OUT/'dev/visual_summary.json',dict(results=summary,
        metric='at least one previously readable neighbouring fragment substantially removed; NOT full removal of all neighbour ink',
        blinded=False,fresh_owner_verdict=False,complete_cleanup_not_established=True,
        native_loss_witnesses_inspected=14,larger_native_contexts_inspected=5))
    paths=sorted((OUT/'dev/review').rglob('*.png'))+sorted((OUT/'dev/witnesses').rglob('*.png'))
    prior.write_json(OUT/'dev/review_artifacts.json',dict(files=[dict(path=str(p.relative_to(OUT)),sha256=prior.file_sha256(p)) for p in paths]))
    print(summary)

if __name__=='__main__':main()
