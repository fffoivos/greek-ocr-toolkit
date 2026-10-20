from PIL import Image, ImageFont
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def font(size,bold=False): return ImageFont.truetype(BOLD if bold else FONT,size)

def paste_fit(canvas,path,box):
    with Image.open(path) as im:
        im=im.convert('RGB'); w,h=box[2]-box[0],box[3]-box[1]
        scale=min(w/im.width,h/im.height)
        size=(max(1,round(im.width*scale)),max(1,round(im.height*scale)))
        im=im.resize(size,Image.Resampling.LANCZOS)
        canvas.paste(im,(box[0]+(w-size[0])//2,box[1]+(h-size[1])//2))
