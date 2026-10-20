import sys
from PIL import Image
src,out,x0,x1,s=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
im=Image.open(src).convert('L')
w,h=im.size
im=im.crop((max(0,x0),0,min(w,x1),h))
im=im.resize((im.size[0]*s,im.size[1]*s),Image.NEAREST)
im.save(out)
