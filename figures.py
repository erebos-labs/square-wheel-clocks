# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Erebos Labs
"""Render measured model data with Pillow; no web assets."""
from pathlib import Path
from math import atan, cos, floor, pi, sinh, sqrt
import json
from PIL import Image, ImageDraw, ImageFont
from model import axle_x, free_speed, parameters, phase, polygon_clearance, radius, road_y, vertices

OUT=Path(__file__).resolve().parent/'output'
OUT.mkdir(exist_ok=True)
BG='#f6f3ea'; INK='#203530'; MUTED='#60716b'; GRID='#dedfd3'; GREEN='#17765c'; AMBER='#b56a17'; RED='#b5443d'; BLUE='#3c6693'

def font(size,serif=False):
    return ImageFont.load_default(size=size)

def text(d,xy,s,size=22,fill=INK,serif=False):
    d.text(xy,s,font=font(size,serif),fill=fill)

def canvas(w,h):
    im=Image.new('RGB',(w,h),BG)
    return im,ImageDraw.Draw(im)

def mapping(box,limits):
    left,top,w,h=box; xmin,xmax,ymin,ymax=limits
    return lambda x,y:(left+(x-xmin)/(xmax-xmin)*w,top+(ymax-y)/(ymax-ymin)*h)

def geometry(d,box,phi,n=4,limits=(-2,2,-1.8,1.8),mark_bad=False):
    left,top,w,h=box
    xmin,xmax,ymin,ymax=limits
    scale=min(w/(xmax-xmin),h/(ymax-ymin))
    xc,yc=(xmin+xmax)/2,(ymin+ymax)/2
    xmin,xmax=xc-w/(2*scale),xc+w/(2*scale)
    ymin,ymax=yc-h/(2*scale),yc+h/(2*scale)
    tr=mapping(box,(xmin,xmax,ymin,ymax))
    d.rectangle((left,top,left+w,top+h),fill='#fffdf7')
    points=[tr(xmin+(xmax-xmin)*i/1200,road_y(xmin+(xmax-xmin)*i/1200,n)) for i in range(1201)]
    d.polygon(points+[tr(xmax,ymin),tr(xmin,ymin)],fill='#d8e4de')
    d.line(points,fill=GREEN,width=4)
    d.line([tr(xmin,0),tr(xmax,0)],fill=MUTED,width=2)
    verts=vertices(phi,n)
    mapped=[tr(*p) for p in verts]
    d.polygon(mapped,fill='#edc98f')
    d.line(mapped+[mapped[0]],fill=INK,width=3)
    center=tr(axle_x(phi,n),0)
    contact=tr(axle_x(phi,n),road_y(axle_x(phi,n),n))
    d.line([center,contact],fill=MUTED,width=2)
    for p,color in ((center,INK),(contact,GREEN)):
        d.ellipse((p[0]-6,p[1]-6,p[0]+6,p[1]+6),fill=color)
    if mark_bad:
        gap,p,_,_=polygon_clearance(phi,n)
        tip=tr(*p);surface=tr(p[0],road_y(p[0],n))
        d.line([tip,surface],fill=RED,width=6)
        d.ellipse((tip[0]-7,tip[1]-7,tip[0]+7,tip[1]+7),fill=RED)
    return tr

def axes(d,box,limits,xticks,yticks,xlabel,ylabel):
    left,top,w,h=box; tr=mapping(box,limits)
    for x,label in xticks:
        px,_=tr(x,0)
        d.line((px,top,px,top+h),fill=GRID,width=1)
        text(d,(px-16,top+h+12),label,18,MUTED)
    for y,label in yticks:
        _,py=tr(0,y)
        d.line((left,py,left+w,py),fill=GRID,width=1)
        text(d,(left-52,py-11),label,18,MUTED)
    d.line((left,top,left,top+h,left+w,top+h),fill=MUTED,width=2)
    text(d,(left+w/2-110,top+h+45),xlabel,20,MUTED)
    text(d,(left,top-36),ylabel,20,MUTED)
    return tr

def line(d,tr,fn,color,width=4):
    d.line([tr(-45+90*i/600,fn((-45+90*i/600)*pi/180)) for i in range(601)],fill=color,width=width)

im,d=canvas(1440,1310)
text(d,(52,32),'EREBOS LABS / NUMERICAL ILLUSTRATION',17,MUTED)
text(d,(52,72),'Square wheels can stay level.',52,INK,True)
text(d,(52,145),'A matching road removes vertical bobbing. Timing remains a separate choice.',25,MUTED)
for j,(deg,label) in enumerate(((-30,'Approaching the crown'),(0,'Face midpoint'),(30,'Approaching the cusp'))):
    x=52+j*454
    text(d,(x,217),label,24,INK,True)
    geometry(d,(x,262,420,378),deg*pi/180)
    text(d,(x,657),f'Wheel angle {deg:+d} degrees; axle y = 0',20,MUTED)
text(d,(52,706),'Apothem a = 1; square side = 2. Each arch spans 1.762747 horizontally but has arc length 2.',21,MUTED)
left=(108,806,565,244)
tr=axes(d,left,(-45,45,0.96,1.46),[(-45,'-45'),(0,'0'),(45,'45')],[(1,'1.0'),(1.2,'1.2'),(1.4,'1.4')],'Wheel phase (degrees)','Forward speed / its minimum')
line(d,tr,lambda p:radius(p),AMBER)
line(d,tr,lambda p:free_speed(p)/free_speed(0),BLUE)
line(d,tr,lambda p:1,GREEN,3)
right=(814,806,565,244)
tr2=axes(d,right,(-45,45,-0.03,0.47),[(-45,'-45'),(0,'0'),(45,'45')],[(0,'0'),(.2,'0.2'),(.4,'0.4')],'Wheel phase (degrees)','Axle rise above midpoint (a)')
line(d,tr2,lambda p:-min(y for x,y in vertices(p))-1,AMBER)
line(d,tr2,lambda p:0,GREEN)
for x,y,color,label in ((108,1142,AMBER,'Constant angular speed'),(108,1173,BLUE,'Free uniform square*'),(108,1204,GREEN,'Constant forward speed'),(814,1142,AMBER,'Square on a flat road'),(814,1173,GREEN,'Matching catenary road')):
    d.line((x,y+10,x+23,y+10),fill=color,width=4);text(d,(x+32,y),label,19,MUTED)
text(d,(52,1260),'*Energy-conserving idealization with maintained contact. Phase is the horizontal axis, not elapsed time.',18,MUTED)
im.save(OUT/'level-is-not-constant-speed.png')

im,d=canvas(1440,1090)
text(d,(52,32),'GEOMETRY CHECK / LOCAL CONTACT AND WHOLE-WHEEL CLEARANCE',17,MUTED)
text(d,(52,72),'A stopped contact point is only one test.',48,INK,True)
text(d,(52,143),'The formal road formula works for both shapes. The triangle still crosses its road.',25,MUTED)
poses=[(4,.55,'Square: clears the road'),(3,.6188937527571892,'Triangle: invalid rigid rolling')]
for j,(n,phi,title) in enumerate(poses):
    x=52+j*702
    text(d,(x,220),title,29,INK,True)
    tr=geometry(d,(x,276,630,630),phi,n,limits=(-2.3,2.7,-2.5,2.5),mark_bad=n==3)
    text(d,(x+16,291),'Same scale: apothem a = 1',19,MUTED)
    text(d,(x+16,601),'Axle y = 0',19,MUTED)
    gap,p,_,_=polygon_clearance(phi,n)
    text(d,(x,928),'Minimum gap: '+('0 (within floating-point roundoff)' if n==4 else f'{gap:.6f} a'),22,RED if n==3 else GREEN)
    text(d,(x,968),'Stationary formal contact is marked green; axle is black.',19,MUTED)
text(d,(52,1023),'2,001 sampled poses per polygon; continuous minimum along every edge. Sampling is not a proof for all poses.',20,MUTED)
text(d,(52,1059),'Author proof and triangle counterexample: Slavik & Wagon, arXiv:2604.03749v3, pp. 4-5. Numerical reconstruction.',17,MUTED)
im.save(OUT/'contact-is-not-clearance.png')

# Two timing choices with the same road, same start/end, and same duration.
# A frame montage is generated for inspection; playback is not asserted.
alpha,b,L=parameters()
frames=[]
N=120
for i in range(N):
    u=i/(N-1)
    phi_top=pi*u
    xbottom=2*L*u
    k=floor((xbottom+b)/L)
    phi_bottom=2*alpha*k+atan(sinh(xbottom-k*L))
    im,d=canvas(960,860)
    text(d,(35,22),'A LEVEL AXLE, TWO CLOCKS',18,MUTED)
    text(d,(35,57),'Same road. Different timing.',39,INK,True)
    for row,(phi,title) in enumerate(((phi_top,'Constant angular speed'),(phi_bottom,'Constant forward speed'))):
        y=142+row*336
        text(d,(35,y),title,25,INK,True)
        geometry(d,(35,y+44,890,264),phi,limits=(-1.5,5,-1.7,1.7))
        _,delta=phase(phi)
        ratio=radius(phi)/(L/(2*alpha)) if row==0 else 1
        color=AMBER if row==0 else GREEN
        text(d,(685,y),f'Speed / mean {ratio:.3f}',20,color)
        d.rectangle((685,y+31,923,y+37),fill=GRID)
        d.rectangle((685,y+31,685+238*ratio/1.3,y+37),fill=color)
        marker=685+238/1.3
        d.line((marker,y+27,marker,y+41),fill=INK,width=2)
    text(d,(35,816),'Model animation: 2 faces per loop; sharp reset to start. No physical ride simulated.',18,MUTED)
    frames.append(im)
frames[0].save(OUT/'two-clocks.gif',save_all=True,append_images=frames[1:],duration=60,loop=0,optimize=False)
montage,_=canvas(1920,1720)
for j,idx in enumerate((0,15,45,75)):
    montage.paste(frames[idx],((j%2)*960,(j//2)*860))
montage.save(OUT/'animation-frame-montage.png')
check={}
for name in ('level-is-not-constant-speed.png','contact-is-not-clearance.png','animation-frame-montage.png','two-clocks.gif'):
    with Image.open(OUT/name) as image:
        check[name]={'dimensions':image.size,'frames':getattr(image,'n_frames',1),'bytes':(OUT/name).stat().st_size}
        if name.endswith('.gif'):
            durations=[]
            for i in range(image.n_frames):
                image.seek(i);durations.append(image.info.get('duration',0));image.load()
            check[name]['total_duration_ms']=sum(durations)
            assert image.n_frames==N
        else:
            image.load()
(OUT/'figure-checks.json').write_text(json.dumps(check,indent=2)+'\n')
print(json.dumps(check,indent=2))
