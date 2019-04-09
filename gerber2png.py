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
    Gb.scale(10)

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
    img = Image.new('RGB',(picx,picy))
    draw = ImageDraw.Draw(img)
    for poly in Gb.solid_geometry:
        try:
            # poly = descartes.patch.PolygonPatch(pyg)
            x, y = poly.exterior.xy
            # print (zip(x,y))
            points = []
            for index in range(len(x)):
                points.append(x[index])
                points.append(y[index])
            # print(points)
            draw.polygon(points, fill=(255,255,255))
            # drawInner(draw, poly, 1)
            # draw.polygon(list(zip(poly.exterior.xy)), fill=(255,255,255))
            for ints in poly.interiors:
                x, y = ints.coords.xy
                points = []
                for index in range(len(x)):
                    points.append(x[index])
                    points.append(y[index])
                # print(points)
                draw.polygon(points, fill=(255, 255, 255))
                # draw.polygon(list(zip(*ints.coords.xy)), fill=(0, 0, 0))
        except:
            traceback.print_exc()
    img.save(path.replace('.','_') + '_bottom.png')
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path.replace('.','_') + '_top.png')
    # img.show()
    layer = Layer(1)
    layer.set_image(img.convert('1'))
    wowfile = WowFile()
    wowfile.layers.append(layer)
    wowfile.Height = layer.height
    wowfile.Width = layer.width
    wowfile.write_wow('D:/user/weiyc/document/altiumProject/洗衣机水位检测/waterCheck/Project Outputs for waterCheck/print.wow')
    mapp = QtGui.QApplication(sys.argv)
    mw = showpng.ImageFrame(path.replace('.','_') + '_top.png')
    mw.show()
    sys.exit(mapp.exec_())
    # showpng.ImageFrame()

if __name__=="__main__":
    toPng('D:/user/weiyc/document/altiumProject/洗衣机水位检测/waterCheck/Project Outputs for waterCheck/PCB1.GTL')