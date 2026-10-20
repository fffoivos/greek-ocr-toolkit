import sys
from PIL import Image
import numpy as np
f=sys.argv[1]; y0,y1,x0,x1=map(int,sys.argv[2:6]); step=int(sys.argv[6]) if len(sys.argv)>6 else 1
import os; T1=int(os.environ.get("T1",100)); T2=int(os.environ.get("T2",180))
a=np.array(Image.open(f).convert('L'))
print(a.shape)
for y in range(y0,min(y1,a.shape[0]),step):
    print('%4d '%y+''.join('#' if a[y,x]<T1 else ('+' if a[y,x]<T2 else '.') for x in range(x0,min(x1,a.shape[1]),step)))
