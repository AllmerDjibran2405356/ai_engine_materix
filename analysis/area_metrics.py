from shapely.geometry import Polygon
def polygon_area_m2(poly: Polygon, scale_m_per_px: float):
    return poly.area * (scale_m_per_px**2)

def polygon_perimeter_m(poly: Polygon, scale_m_per_px: float):
    return poly.length * scale_m_per_px
