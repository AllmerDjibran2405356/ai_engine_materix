import cv2, math
from shapely.geometry import LineString, Polygon
from shapely.ops import linemerge, unary_union, polygonize
import numpy as np
from typing import List, Tuple

def detect_line_segments(th_binary, min_len=30):
    edges = cv2.Canny(th_binary, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, math.pi/180, threshold=60, minLineLength=min_len, maxLineGap=20)
    segs = []
    if lines is None:
        return segs
    for l in lines:
        x1,y1,x2,y2 = l[0]
        segs.append(((int(x1),int(y1)),(int(x2),int(y2))))
    return segs

def merge_and_polygonize(segs):
    if not segs:
        return [], []
    lines = [LineString([a,b]) for a,b in segs if a!=b]
    u = unary_union(lines)
    merged = linemerge(u)
    polys = list(polygonize(merged))
    return merged, polys

def snap_and_clean_polys(polys, min_area_px=1500):
    # keep only large polygons likely rooms
    return [p for p in polys if p.area >= min_area_px]
