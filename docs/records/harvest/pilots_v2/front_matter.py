"""Additional IA title/contents witnesses after covers were found in first leaves.

The original read pages stay in every denominator. Five additional leaves per
book keep each IA document below the brief's 40-page ceiling (35--39 pages).
"""
from pilotlib import *
from acquire import IA

if __name__=='__main__':
    c=client('ia')
    for pilot,item,count in IA:
        for n in range(6,11):
            try:
                r=raster(pilot,item,n,f'https://archive.org/download/{item}/page/n{n-1}.jpg',c,'front')
                r['sample_extension_reason']='native sheet showed bindings/covers in earliest leaves; add actual front matter, preserve original pages in read denominator'
                write(BASE/'receipts/pages'/(r['id']+'.json'),r);print(pilot,item,n,'ok',flush=True)
            except Exception as e:print(item,n,type(e).__name__,str(e)[:150],flush=True)
