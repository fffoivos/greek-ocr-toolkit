import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('L')
x0,x1,y0,y1=map(int,sys.argv[2:6]); t=int(sys.argv[6]) if len(sys.argv)>6 else 128
for y in range(y0,min(y1,im.size[1])):
  print('%3d '%y+''.join('#' if im.getpixel((x,y))<t else ('+' if im.getpixel((x,y))<t+50 else '.') for x in range(x0,min(x1,im.size[0]))))
