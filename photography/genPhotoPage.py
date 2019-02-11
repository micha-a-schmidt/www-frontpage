import os, sys,shutil
from PIL import ImageOps, Image, ExifTags, ImageChops
from multiprocessing import Pool 
#from galleryPresets import *


REGENERATE = False
if len(sys.argv)>1:
    if sys.argv[1]=="regen":
        REGENERATE=True
#REGENERATE = False

if REGENERATE:
    print("pictures will be regenerated\n")
else:
    print("pictures will NOT be regenerated\n")

gallery='pics'
target="../content/home/photography.md"
targetdir="../static/img/selection"
sourcedir="/mnt/Multimedia/Pictures"
# if len(sys.argv)>2:
    # gallery=sys.argv[1]
#     target=sys.argv[2]
jobs=[]


class preset():
    name=""
    action=""
    height=0
    width=0
    center=(0.5,0.5)
    def __init__(self, name, action, width, height):
        self.name=name
        self.action=action
        self.height=height
        self.width=width

presets=[preset("","pad",1024,768), preset("-thumb","fit",150,150) ]

#thumbdir=[ p.name for p in presets ]

templateHeader="""---
title: "Photography"
---

{{< gallery >}}
"""

templatePic="{{{{< figure link=\"/img/selection/pic{num}.jpg\" thumb=\"-thumb\" size=\"1024x768\" >}}}}\n"

templateFooter="{{< /gallery >}} {{< load-photoswipe >}}"


def processImage(job_details): 
    p, counter, source, outdir = job_details
    try:
        with Image.open(source) as im:
            for orientation in ExifTags.TAGS.keys(): 
                if ExifTags.TAGS[orientation]=='Orientation': 
                    break 
            try:
                exif=dict(im._getexif().items())
                if exif[orientation] == 3 :
                    im = im.rotate(180, expand=True)
                elif exif[orientation] == 6 : 
                    im=im.rotate(270, expand=True)
                elif exif[orientation] == 8 : 
                    im=im.rotate(90, expand=True)
            except Exception as e:
                print("Exif exception: ",e)

            if p.action == "fit":
                im = ImageOps.fit(im,(p.width,p.height,), method=Image.ANTIALIAS, centering=p.center)
            elif p.action == "pad":
                im.thumbnail((p.width,p.height),Image.ANTIALIAS)
                image_size=im.size
                thumb = im.crop( (0,0,p.width,p.height))
                offset_x = int(max((p.width - image_size[0])/2,0))
                offset_y = int(max((p.height - image_size[1])/2,0))
                im = ImageChops.offset(thumb,offset_x,offset_y)
            elif p.action == "resize":
                (w,h) = im.size
                if h>w and p.height<p.width:
                    wnew=int(p.width*w/h)
                    hnew=p.height
                    im = ImageOps.fit(im,(wnew,hnew,), method=Image.ANTIALIAS, centering=p.center)
                elif h<w and p.height>p.width:
                    wnew=p.width
                    hnew=int(p.height*h/w)
                    im = ImageOps.fit(im,(wnew,hnew,), method=Image.ANTIALIAS, centering=p.center)
                else:
                    im = ImageOps.fit(im,(p.width,p.height,), method=Image.ANTIALIAS, centering=p.center)
            elif p.action == "thumb":
                im.thumbnail((p.width,p.height),Image.ANTIALIAS)
            if not(os.path.exists(outdir)):
                try:
                    os.mkdir(outdir)
                except Exception:
                    print("{0} exists".format(outdir))
            im.save(os.path.join(outdir,"pic{num}{suffix}.jpg".format(num=counter,suffix=p.name)),"JPEG")
            im.close()
        return 'OK'
    except Exception as e: 
        print(source)
        return e 

# generate resize jobs
with open(target,"w") as out:
    out.write(templateHeader)
    with open(gallery) as f:
        for counter,pic in enumerate(f):
            # write target....
            if pic.isspace():
                continue
            out.write(templatePic.format(num=counter))
            for p in presets:
                jobs.append((p,counter,os.path.join(sourcedir,pic.rstrip()),targetdir))
    out.write(templateFooter)

if REGENERATE and len(jobs)>0:
    print("submitting {0} jobs".format(len(jobs)))

    pool = Pool(4)
    results = pool.map(processImage, jobs)
    if 'OK' in results:
        results=results.remove('OK')
    if results==None:
        print("No errors")
    else:
        print("{0} errors\n".format(len(results)))
        print(results)

print("...finished")
