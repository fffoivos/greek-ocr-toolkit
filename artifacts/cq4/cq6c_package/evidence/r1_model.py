"""Small four-stage residual mark reader, grey + recogniser-span mask."""
import torch
from torch import nn

from scripts.labelfix.clariden.r1_common import HEADS, LETTERS


class Block(nn.Module):
    def __init__(self, incoming, channels, stride=1):
        super().__init__()
        middle = max(8, (channels*7//8)//8*8)
        self.body=nn.Sequential(nn.Conv2d(incoming,middle,3,stride,1,bias=False),nn.BatchNorm2d(middle),nn.ReLU(),
                                nn.Conv2d(middle,channels,3,1,1,bias=False),nn.BatchNorm2d(channels))
        self.skip=nn.Identity() if incoming==channels and stride==1 else nn.Sequential(
            nn.Conv2d(incoming,channels,1,stride,bias=False),nn.BatchNorm2d(channels))
        self.relu=nn.ReLU()

    def forward(self,x):
        return self.relu(self.body(x)+self.skip(x))


class MarkReader(nn.Module):
    def __init__(self, embedding=True):
        super().__init__()
        self.embedding=nn.Embedding(len(LETTERS),64) if embedding else None
        layers=[nn.Conv2d(2,32,5,2,2,bias=False),nn.BatchNorm2d(32),nn.ReLU(),nn.MaxPool2d(3,2,1)]
        incoming=32
        for i,channels in enumerate((32,64,128,192)):
            layers.extend([Block(incoming,channels,1 if i==0 else 2),Block(channels,channels)])
            incoming=channels
        layers.extend([nn.AdaptiveAvgPool2d(1),nn.Flatten()])
        self.backbone=nn.Sequential(*layers)
        self.mlp=nn.Sequential(nn.Linear(192+(64 if embedding else 0),256),nn.ReLU())
        self.heads=nn.ModuleList(nn.Linear(256,len(c)) for c in HEADS.values())

    def forward(self,x,letter):
        x=self.backbone(x)
        if self.embedding is not None:
            x=torch.cat((x,self.embedding(letter)),dim=1)
        x=self.mlp(x)
        return [h(x) for h in self.heads]


def flop_estimate(model):
    """Count multiply + add as two FLOPs, real 2x64x128 input; train ~=3x forward."""
    count=[0];hooks=[]
    def hook(m, args, out):
        if isinstance(m,nn.Conv2d):
            count[0]+=out.numel()*(m.in_channels//m.groups)*m.kernel_size[0]*m.kernel_size[1]*2
        elif isinstance(m,nn.Linear): count[0]+=out.numel()*m.in_features*2
    for m in model.modules():
        if isinstance(m,(nn.Conv2d,nn.Linear)):hooks.append(m.register_forward_hook(hook))
    training=model.training;model.eval()
    with torch.no_grad():model(torch.zeros(1,2,64,128),torch.zeros(1,dtype=torch.long))
    model.train(training)
    for h in hooks:h.remove()
    return dict(parameters=sum(p.numel() for p in model.parameters()),forward_flops=count[0],
                approximate_train_flops=count[0]*3,convention='conv/linear multiply+add=2; backward about 2x forward')
