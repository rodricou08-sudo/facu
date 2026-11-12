import sys
from PIL import Image, ImageDraw, ImageFont
S=sys.argv[1]; O=f"{S}/e875"
F9=f"{S}/fonts/Montserrat-900.ttf"; F8=f"{S}/fonts/Montserrat-800.ttf"
TF=ImageFont.truetype(F9,56); LF=ImageFont.truetype(F8,47)
def wrap(d,txt,font,maxw):
    words=txt.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def band(name,h,label,lcolor=(255,212,0,255)):
    img=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.rectangle([0,0,1079,h-1],fill=(0,0,0,255))
    y=105
    for txt,bg in [("5 ERRORES QUE TE HACEN",(255,255,255,255)),("PARECER MENOS INTELIGENTE",(255,212,0,255))]:
        bb=d.textbbox((0,0),txt,font=TF); w,hh=bb[2]-bb[0],bb[3]-bb[1]; px,py=30,18
        x0=(1080-w)//2-px
        d.rounded_rectangle([x0,y,x0+w+2*px,y+hh+2*py],radius=20,fill=bg)
        d.text(((1080-w)//2-bb[0],y+py-bb[1]),txt,font=TF,fill=(0,0,0,255))
        y+=hh+2*py+12
    y+=22
    for ln in wrap(d,label,LF,960):
        bb=d.textbbox((0,0),ln,font=LF); w=bb[2]-bb[0]
        d.text(((1080-w)//2-bb[0],y-bb[1]),ln,font=LF,fill=lcolor)
        y+=(bb[3]-bb[1])+14
    img.save(f"{O}/{name}.png"); print(name,"text bottom",y,"band",h)
band("intro",560,"(MIRALO HASTA EL FINAL)")
band("s1",452,"1. OPINAR DE ABSOLUTAMENTE TODO")
band("s2",452,"2. NO DEJAR TERMINAR LAS FRASES")
band("s3",452,"3. CONFUNDIR PALABRAS DIFÍCILES CON INTELIGENCIA")
band("s4",452,"4. DEFENDER TUS OPINIONES A MUERTE SIN RAZÓN")
band("s5",452,"5. INVENTAR RESPUESTAS CUANDO NO SABÉS")
band("outro",452,"SEGUIME PARA MÁS VALOR")
