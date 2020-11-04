import bpy
import math
import numpy as np
import itertools
import bmesh
from typing import List
import sys
import random

#Creates layer and assigns name. Returns layer object. 
def gp_create_layer(gpencil: bpy.types.GreasePencil, gpencil_layer_name='GP_Layer',
                            clear_layer=False) -> bpy.types.GPencilLayer:

    # Get draw layer if already exists or creates one of necessary
    if gpencil.data.layers and gpencil_layer_name in gpencil.data.layers:
        gpencil_layer = gpencil.data.layers[gpencil_layer_name]
    else:
        gpencil_layer = gpencil.data.layers.new(gpencil_layer_name, set_active=True)
    
    # Option to clear previous layer data and reset canvas
    if clear_layer:
        gpencil_layer.clear()  

    return gpencil_layer

#Creates grease pencil object and assigns name. Returns grease pencil object.    
def gp_create(gp_obj_name='GPencil') -> bpy.types.GreasePencil:

    # Create grease pencil if doesn't exist
    if gp_obj_name not in bpy.context.scene.objects:
        # assign starting point at (0,0,0)
        bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
        
        # rename grease pencil
        bpy.context.scene.objects[-1].name = gp_obj_name

    # Gets newly created grease pencil or one that already exists
    gpencil = bpy.context.scene.objects[gp_obj_name]

    return gpencil

# Combines gp_create and gp_layer create
def init_grease_pencil(gp_obj_name='GPencil', gpencil_layer_name='GP_Layer',
                       clear_layer=True) -> bpy.types.GPencilLayer: 
    gpencil = gp_create(gp_obj_name)
    gpencil_layer = gp_create_layer(gpencil, gpencil_layer_name, clear_layer=clear_layer)
    return gpencil_layer
    
# draws grease pencil line between two points
def draw_line(gp_frame, p0: tuple, p1: tuple):
    # Create new stroke
    gp_stroke = gp_frame.strokes.new()
    # Ensure that creation space is 3D for creating shapes later on
    gp_stroke.display_mode = '3DSPACE'  
    
    # define endpoints for line
    gp_stroke.points.add(count=2)
    gp_stroke.points[0].co = p0
    gp_stroke.points[1].co = p1
    return gp_stroke

#draws basic shape using draw line function
def draw_shape(gp_frame, verts):
    gp_stroke = gp_frame.strokes.new()
    # Ensure that creation space is 3D for creating shapes later on
    gp_stroke.display_mode = '3DSPACE' 
    gp_stroke.points.add(count = len(verts))
    for i in range (len(verts)):
        gp_stroke.points[i].co = verts[i]
    return gp_stroke

gp_layer = init_grease_pencil()
gp_frame = gp_layer.frames.new(1)


# define variables
size = 50
width, height = size, size
n_step = 1

# draws single tile of pattern
# random values determine whether or not a line is diagonal
def draw_tile (x, y , x2, y2):
    if random.random() >= 0.5:
        verts = draw_line([x, y, 0], [x + x2, y + y2, 0])
    else:
        #verts = line([x + x2, y, 0], [x + x2, y + y2, 0])
        verts = line([x + x2, y, 0], [x, y + y2, 0]) 
    draw_shape (gp_frame, verts)

# nested for loop draws tiles across range of size value   
for i in range (0, size, n_step):
    for j in range(0, size, n_step):
        draw_tile(i, j, n_step, n_step)
        
        


def draw_square(gp_frame, center: tuple, size: int, material_index=0):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    #3D spaced must be enabled for future editing
    gp_stroke.display_mode = '3DSPACE'  
    gp_stroke.draw_cyclic = True        # closes the stroke
    gp_stroke.material_index = material_index

    # Define stroke geometry
    radius = size / 2
    gp_stroke.points.add(count=4)
    gp_stroke.points[0].co = (center[0] - radius, center[1] - radius, center[2])
    gp_stroke.points[1].co = (center[0] - radius, center[1] + radius, center[2])
    gp_stroke.points[2].co = (center[0] + radius, center[1] + radius, center[2])
    gp_stroke.points[3].co = (center[0] + radius, center[1] - radius, center[2])
    return gp_stroke

def draw_cube(gp_frame, center: tuple, size: float, material_index=0):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = '3DSPACE'  # allows for editing
    gp_stroke.draw_cyclic = True  # closes the stroke
    gp_stroke.material_index = material_index

    # Define stroke geometry
    radius = size/2
    offsets = list(itertools.product([1, -1], repeat=3))  # vertices offset-product from the center
    points = [(center[0] + radius * offset[0],
               center[1] + radius * offset[1],
               center[2] + radius * offset[2]) for offset in offsets]
    stroke_idx = [0, 4, 6, 2, 0, 1, 5, 7, 3, 1, 5, 4, 6, 7, 3, 2]

    gp_stroke.points.add(count=len(stroke_idx))
    for i, idx in enumerate(stroke_idx):
        gp_stroke.points[i].co = points[idx]

    return gp_stroke

def draw_circle(gp_frame, center: tuple, radius: float, segments: int):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = '3DSPACE'  # allows for editing
    gp_stroke.draw_cyclic = True        # closes the stroke
    
    #gp_stroke.line_width = 100
    #gp_stroke.material_index = 1

    # Define stroke geometry
    angle = 2*math.pi/segments  # angle in radians
    gp_stroke.points.add(count=segments)
    for i in range(segments):
        x = center[0] + radius*math.cos(angle*i)
        y = center[1] + radius*math.sin(angle*i)
        z = center[2]
        gp_stroke.points[i].co = (x, y, z)

    return gp_stroke

def rotate_stroke(stroke, angle, axis='z'):
    # Define rotation matrix based on axis
    if axis.lower() == 'x':
        transform_matrix = np.array([[1, 0, 0],
                                     [0, math.cos(angle), -math.sin(angle)],
                                     [0, math.sin(angle), math.cos(angle)]])
    elif axis.lower() == 'y':
        transform_matrix = np.array([[math.cos(angle), 0, -math.sin(angle)],
                                     [0, 1, 0],
                                     [math.sin(angle), 0, math.cos(angle)]])
    # default on z
    else:
        transform_matrix = np.array([[math.cos(angle), -math.sin(angle), 0],
                                     [math.sin(angle), math.cos(angle), 0],
                                     [0, 0, 1]])

    # Apply rotation matrix to each point
    for i, p in enumerate(stroke.points):
        p.co = transform_matrix @ np.array(p.co).reshape(3, 1)

def draw_sphere(gp_frame, center: tuple, radius: int, circles: int):
    angle = math.pi / circles
    for i in range(circles):
        circle = draw_circle(gp_frame, center, radius, 32)
        rotate_stroke(circle, angle*i, 'x')
        print(angle * i)


def squares_grid(gp_frame, nb_rows: int, nb_cols: int,
                 rand_size=False, rand_rotation=False, material_index=0):
    for x in range(nb_cols):
        for y in range(nb_rows):
            center = (x, y, 0)
            if rand_size:
                radius = (x % (nb_cols/2) * y % (nb_rows/2))/((nb_cols/2)*(nb_rows/2)) + np.random.rand()/2
            else:
                radius = 1
            gp_stroke = draw_square(gp_frame, center, radius, material_index=material_index)
            draw_cube(gp_frame, center, radius)
            if rand_rotation:
                rotate_stroke(gp_stroke, np.random.rand())


def _get_midpoint(p0: tuple, p1:tuple):
    return (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2


def polygon_recursive(gp_frame, polygon, step=0, max_steps=3):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = '3DSPACE'  # allows for editing
    gp_stroke.draw_cyclic = True  # closes the stroke
    gp_stroke.material_index = step
    # Define stroke geometry
    gp_stroke.points.add(count=len(polygon))
    for i, p in enumerate(polygon):
        gp_stroke.points[i].co = p
    if step >= max_steps:
        return
    else:
        new_polygon = []
        midpoints = []
        for i in range(len(polygon)):
            p0 = polygon[i]
            p1 = polygon[0] if i == len(polygon)-1 else polygon[i+1]
            opposite_point = (0, 0, 0)
            midpoint = _get_midpoint(p0, p1)
            new_point = _get_midpoint(opposite_point, midpoint)
            for i in range(step):
                new_point = _get_midpoint(new_point, midpoint)
            new_polygon.append(new_point)
            midpoints.append(midpoint)
        polygon_recursive(gp_frame, new_polygon, step+1, max_steps)
        for i in range(len(polygon)):
            other_polygon = [polygon[i], midpoints[i-1], new_polygon[i-1], new_polygon[i], midpoints[i]]
            polygon_recursive(gp_frame, other_polygon, step + 1, max_steps)
            

def draw_polygon_fractal(gp_frame, polygon_sides: int):
    # Define base polygon
    angle = 2*math.pi/polygon_sides  # angle in radians
    polygon = []
    for i in range(polygon_sides):
        x = 3*math.cos(angle*i)
        y = 3*math.sin(angle*i)
        z = 3
        polygon.append((x, y, z))
    polygon_recursive(gp_frame, polygon, max_steps=5)




NUM_FRAMES = 100
FRAMES_SPACING = 1
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = NUM_FRAMES*FRAMES_SPACING


def animate_square_sliding(gp_layer):
    main_size = 4
    positions = np.linspace(-main_size / 2, main_size / 2, num=NUM_FRAMES)
    for frame in range(1, NUM_FRAMES):
        gp_frame = gp_layer.frames.new(frame*FRAMES_SPACING)
        _ = draw_square(gp_frame, (0, 0, 0), main_size)

        draw_square(gp_frame, (main_size/2+0.5, positions[frame], 0), 1)



    
def draw_multiple_circles_animated(gp_layer):
    for frame in range(1, NUM_FRAMES):
        gp_frame = gp_layer.frames.new(frame)
        for i in range(15):
            radius = np.random.randint(1, 7) + np.random.rand()
            draw_circle(gp_frame, (0, 0, 0), radius, 80)

def grid_animation(gp_layer):
    for frame in range(1, NUM_FRAMES):
        gp_frame = gp_layer.frames.new(frame)
        for i in range(15):
            #radius = np.random.randint(1, 7) + np.random.rand()
            squares_grid(gp_frame, 10, 10, rand_size=True, rand_rotation=False, material_index=1)

def line_animation(gp_layer):
    x = 0
    y = 0
    z = 0
    for frame in range(1, NUM_FRAMES):
        gp_frame = gp_layer.frames.new(frame)
        while x < 60:
           draw_line(gp_frame, (x, y, z), (x+1, y+1, z))
           x+=1
           y+=1
def translate_stroke(stroke, vector):
    for i, p in enumerate(stroke.points):
        p.co = np.array(p.co) + vector
    
    
    
    
    
    
    
    
def kinetic_rotation_polygon(gp_layer, center: tuple, nb_polygons: int, nb_sides: int,
                    min_radius: float, max_radius: float,
                    nb_frames: int):
    radiuses = np.linspace(min_radius, max_radius, nb_polygons)
    #radiuses = np.random.rand(nb_polygons)*(max_radius - min_radius) + min_radius  # randomized radiuses
    main_angle = (2*math.pi)/nb_frames

    # Animate polygons across frames
    for frame in range(1, nb_frames):
        gp_frame = gp_layer.frames.new(frame)
        for i in range(nb_polygons):
            #polygon = draw_circle(gp_frame, (0, 0, 0), radiuses[i], nb_sides[i])
            polygon = draw_circle(gp_frame, (0, 0, 0), radiuses, nb_sides)
            #cur_angle = ((len(radiuses) - i) * (2 * pi)) / nb_frames
            cur_angle = ((len(radiuses) - i) // 2 * (2 * math.pi)) / nb_frames
            for axis in ['x']:
                rotate_stroke(polygon, cur_angle*frame, axis=axis)
            translate_stroke(polygon, center)
    
