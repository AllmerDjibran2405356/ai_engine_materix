import math
from typing import Dict, List

def estimate_from_rooms(room_list: List[Dict], wall_list: List[Dict], floor_area_m2: float) -> Dict:
    # room_list contains dicts {'id', 'area_m2', 'perimeter_m', 'polygon_coords_m'}
    totals = {}
    totals['total_floor_area_m2'] = round(floor_area_m2,3)
    total_wall_area = sum(w.get('length_m',0.0) * w.get('height_m',3.0) for w in wall_list)
    totals['total_wall_area_m2'] = round(total_wall_area,3)
    totals['estimated_bricks'] = math.ceil(totals['total_wall_area_m2'] * 50)
    totals['foundation_m3'] = round(floor_area_m2 * 0.3,3)
    totals['cement_bags'] = math.ceil(totals['foundation_m3'] * 8)
    return totals

def breakdown_walls_per_section(walls_shapely_list, scale):
    # create labeled walls A,B,C... by ordering; returns list of dict per wall segment
    out=[]
    import string
    labels = string.ascii_uppercase
    for i,w in enumerate(walls_shapely_list):
        out.append({
            'id': labels[i%len(labels)],
            'length_m': round(w.length * scale,3),
            'height_m': 3.0
        })
    return out
