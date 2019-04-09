import math
import sys

from PyQt4 import QtGui

import camlib
import traceback

import showpng
from genWowFile import Layer,WowFile


def toPng(path):
    Gb = camlib.Gerber()

    Gb.parse_file(path)
    Gb.convert_units('mm')
    # Gb.scale(1000/54)
    Gb.scale(854/98.637)

    import numpy as np
    from PIL import Image, ImageDraw
    from shapely.geometry import Point

    picx = 0
    picy = 0

    for poly in Gb.solid_geometry:
        try:
            # poly = descartes.patch.PolygonPatch(pyg)
            x, y = poly.exterior.xy
            for item in x:
                if item > picx:
                    picx = item
            for item in y:
                if item > picy:
                    picy = item
        except:
            pass
    picx = int(math.ceil(picx))
    picy = int(math.ceil(picy))
    print('image size:',picx,picy)
    offsetx = int((854 - picx)/2)
    offsety = int((480 - picy)/2)
    img = Image.new('RGB',(854, 480))
    draw = ImageDraw.Draw(img)
    points = [0,0,854,0,854,480,0,480,0,0]
    draw.polygon(points, fill=(0, 0, 0))
    for poly in Gb.solid_geometry:
        try:
            # poly = descartes.patch.PolygonPatch(pyg)
            x, y = poly.exterior.xy
            # print (zip(x,y))
            points = []
            for index in range(len(x)):
                points.append(x[index] + offsetx)
                points.append(y[index] + offsety)
            # print(points)
            draw.polygon(points, fill=(255,255,255))
            # drawInner(draw, poly, 1)
            # draw.polygon(list(zip(poly.exterior.xy)), fill=(255,255,255))
            for ints in poly.interiors:
                x, y = ints.coords.xy
                points = []
                for index in range(len(x)):
                    points.append(x[index] + offsetx)
                    points.append(y[index] + offsety)
                # print(points)
                draw.polygon(points, fill=(255, 255, 255))
                # draw.polygon(list(zip(*ints.coords.xy)), fill=(0, 0, 0))
        except:
            traceback.print_exc()
    img.save(path.replace('.','_') + '_bottom.png')
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path.replace('.','_') + '_top.png')
    # img.show()
    # img = img.convert('L')  # convert image to monochrome - this works
    img = img.convert('1')  # convert image to black and white
    # img = img.convert('1;R')
    # img = img.convert('1')
    img.save(path.replace('.','_') + '_top1.png')
    layer = Layer(1)
    layer.set_image(img)
    wowfile = WowFile()
    wowfile.layers.append(layer)
    wowfile.Height = 854
    wowfile.Width = 480
    wowfile.write_wow('print.wow')
    # mapp = QtGui.QApplication(sys.argv)
    # mw = showpng.ImageFrame(path.replace('.','_') + '_top1.png')
    # mw.show()
    # sys.exit(mapp.exec_())
    # showpng.ImageFrame()

if __name__=="__main__":
    toPng('gerber/PCB1.GTL')