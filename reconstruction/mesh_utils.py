import trimesh
def merge_scene(scene: trimesh.Scene):
    # return combined mesh
    combined = trimesh.util.concatenate([g for g in scene.geometry.values()]) if scene.geometry else None
    return combined
