from shapely.geometry import Polygon
from shapely.affinity import scale as shapely_scale
import trimesh
from typing import List

def scale_polygon_to_meters(poly: Polygon, scale_m_per_px: float):
    return shapely_scale(poly, xfact=scale_m_per_px, yfact=scale_m_per_px, origin=(0,0))

def extrude_polygon(poly_m: Polygon, height_m: float):
    mesh = trimesh.creation.extrude_polygon(poly_m, height_m)
    return mesh

def build_scene_from_polygons(polys_m, height_m):
    meshes = []
    for p in polys_m:
        try:
            m = extrude_polygon(p, height_m)
            meshes.append(m)
        except Exception:
            continue
    scene = trimesh.Scene(meshes)
    return scene
