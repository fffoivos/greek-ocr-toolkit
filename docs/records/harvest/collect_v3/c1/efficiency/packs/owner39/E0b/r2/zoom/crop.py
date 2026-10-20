import sys
from PIL import Image
f,out=sys.argv[1:3]; y,x,h,w,s=map(int,sys.argv[3:8])
im=Image.open(f).convert('L').crop((x,y,x+w,y+h))
im.resize((w*s,h*s),Image.LANCZOS).save(out)
