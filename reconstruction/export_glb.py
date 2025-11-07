import trimesh
from pathlib import Path

def export_scene(scene: trimesh.Scene, out_path: str, file_type='glb'):
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if file_type.lower()=='glb':
        data = scene.export(file_type='glb')
        with open(p, 'wb') as fh:
            fh.write(data)
    else:
        scene.export(str(p))
    return str(p)
