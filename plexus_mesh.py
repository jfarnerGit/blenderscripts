import bpy

# delete default cube if exists
if "Cube" in bpy.data.meshes:
    mesh = bpy.data.meshes["Cube"]
    print("removing mesh", mesh)
    bpy.data.meshes.remove(mesh)

context = bpy.context
scene = context.scene

# adding plane with default size features
bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

# quickly resize mesh with new scale if necessary
bpy.ops.transform.resize(value=(15, 15, 15), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), \
                         orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False,
                         proportional_edit_falloff='SMOOTH', proportional_size=1, \
                         use_proportional_connected=False, use_proportional_projected=False)

# apply newly created scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# subdivide mesh to create more faces, which allows for more granular detail later on.
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.subdivide(number_cuts=100)
bpy.ops.object.editmode_toggle()

mesh_obs = [o for o in scene.objects if o.type == 'MESH']

# function for assigning modifiers to objects in Blender
def delmods(ob, mod_type="ALL"):
    mods = (ob.modifiers[:] if mod_type == "ALL"
            else [m for m in ob.modifiers if m.type == mod_type])
    while (mods):
        ob.modifiers.remove(mods.pop())


# add decimate modifier to create geometric pattern between faces
for ob in mesh_obs:
    delmods(ob, 'DECIMATE')
    dm = ob.modifiers.new("deci", type='DECIMATE')
    dm.ratio = 0.05  # change to suit - this value controls number of triangles - shoulod be between .01 - .05 for best results. lower value for fewer triangles
    bpy.ops.object.modifier_apply(modifier="deci")

# adding empty object that will be rigged to animate mesh
bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

# adding displacement modifier which allows plane to be animated in 3D by section 
for ob in mesh_obs:
    delmods(ob, 'DISPLACE')
    ds = ob.modifiers.new("disp", type='DISPLACE')

    # assigning Cloud texture as displacement modifier to create peaks and valleys in animation
    cTex = bpy.data.textures.new("Texture", type='CLOUDS')
    cTex.noise_scale = 2
    cTex.noise_depth = 0

    ds.texture = cTex

    ds.texture_coords = 'OBJECT'
    ds.texture_coords_object = bpy.data.objects["Empty"]

# add sphere to be used as node model - parent sphere is placed well outside of the mesh
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(30, 30, 0),
                                     scale=(1, 1, 1))

# creating particle system
for ob in mesh_obs:
    delmods(ob, 'PARTICLE_SYSTEM')
    pt = ob.modifiers.new("part", type='PARTICLE_SYSTEM')
    bpy.data.particles['part'].type = 'HAIR'
    bpy.data.particles['part'].emit_from = 'VERT'
    bpy.data.particles['part'].render_type = 'OBJECT'
    bpy.data.particles['part'].instance_object = bpy.data.objects["Sphere"]
    bpy.data.particles['part'].particle_size = 0.01  # resizing particles
    bpy.data.particles['part'].count = 2500  # filling in missing nodes

 
# applying wireframe modifier to the mesh     
for ob in mesh_obs:
    delmods(ob, 'WIREFRAME')
    wf = ob.modifiers.new("wire", type='WIREFRAME')
