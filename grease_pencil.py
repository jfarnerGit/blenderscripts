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
    # Ensure that creation space is 3D to enable editing
    gp_stroke.display_mode = '3DSPACE'  
    
    # define endpoints for line
    gp_stroke.points.add(count=2)
    gp_stroke.points[0].co = p0
    gp_stroke.points[1].co = p1
    return gp_stroke

#draws basic shape using draw line function
def draw_shape(gp_frame, verts):
    gp_stroke = gp_frame.strokes.new()
    # Ensure that display mode is 3D to enable editing
    gp_stroke.display_mode = '3DSPACE' 
    gp_stroke.points.add(count = len(verts))
    for i in range (len(verts)):
        gp_stroke.points[i].co = verts[i]
    return gp_stroke

gp_layer = init_grease_pencil()
gp_frame = gp_layer.frames.new(1)




# draws single tile of pattern
# random values determine whether or not a line is diagonal
def draw_tile (x, y , x2, y2):
    if random.random() >= 0.5:
        verts = draw_line([x, y, 0], [x + x2, y + y2, 0])
    else:
        #verts = line([x + x2, y, 0], [x + x2, y + y2, 0])
        verts = line([x + x2, y, 0], [x, y + y2, 0]) 
    draw_shape (gp_frame, verts)

'''
#Remove comment quotes to draw generative tiled art

# define variables for creating tiles
size = 50
width, height = size, size
n_step = 1
    
# nested for loop draws tiles across range of size value   
for i in range (0, size, n_step):
    for j in range(0, size, n_step):
        draw_tile(i, j, n_step, n_step)
'''        
        

# Draws square based around a center point
def draw_square(gp_frame, center: tuple, size: int, material_index=0):
    gp_stroke = gp_frame.strokes.new()
    
    #3D spaced must be enabled for future editing
    gp_stroke.display_mode = '3DSPACE'
    
    #enable cyclic drawing to close the shape
    gp_stroke.draw_cyclic = True        
    gp_stroke.material_index = material_index

    # define stroke geometry for each edge of the square
    radius = size / 2
    gp_stroke.points.add(count=4)
    
    # offset strokes from center point
    gp_stroke.points[0].co = (center[0] - radius, center[1] - radius, center[2])
    gp_stroke.points[1].co = (center[0] - radius, center[1] + radius, center[2])
    gp_stroke.points[2].co = (center[0] + radius, center[1] + radius, center[2])
    gp_stroke.points[3].co = (center[0] + radius, center[1] - radius, center[2])
    return gp_stroke

# Uses same logic from draw_square() to draw cube around center point
def draw_cube(gp_frame, center: tuple, size: float, material_index=0):
    gp_stroke = gp_frame.strokes.new()
    
    # Ensure that creation space is 3D to enable editing
    gp_stroke.display_mode = '3DSPACE' 
   
    # Enable cyclic drawing to close close the shape
    gp_stroke.draw_cyclic = True  
    gp_stroke.material_index = material_index

    # Define stroke geometry
    radius = size/2
    
    # Define offset
    os = list(itertools.product([1, -1], repeat=3))  
    
    # Offset vertices from center of cube
    points = [(center[0] + radius * os[0],
               center[1] + radius * os[1],
               center[2] + radius * os[2]) for offset in os]
    stroke_index = [0, 4, 6, 2, 0, 1, 5, 7, 3, 1, 5, 4, 6, 7, 3, 2]

    gp_stroke.points.add(count=len(stroke_index))
    for i, idx in enumerate(stroke_index):
        gp_stroke.points[i].co = points[idx]

    return gp_stroke

#draws circle around a center point
def draw_circle(gp_frame, center: tuple, radius: float, segments: int):
    gp_stroke = gp_frame.strokes.new()
    
    # Ensure that creation space is 3D to enable editing
    gp_stroke.display_mode = '3DSPACE'  
    
    # Enable cyclic drawing to close close the shape
    gp_stroke.draw_cyclic = True      
  
    
    # Convert angle to radians
    angle = 2*math.pi/segments  
    gp_stroke.points.add(count=segments)
    
    # Draw segments rotating around center point
    for i in range(segments):
        x = center[0] + radius*math.cos(angle*i)
        y = center[1] + radius*math.sin(angle*i)
        z = center[2]
        gp_stroke.points[i].co = (x, y, z)

    return gp_stroke

def rotate_stroke(stroke, angle, axis='z'):
    
    # Define rotation matrix based on axis
    if axis.lower() == 'x':
        transform_matrix = np.array([[1, 0, 0], [0, math.cos(angle), -math.sin(angle)], [0, math.sin(angle), math.cos(angle)]])
    
    elif axis.lower() == 'y':
        transform_matrix = np.array([[math.cos(angle), 0, -math.sin(angle)], [0, 1, 0], [math.sin(angle), 0, math.cos(angle)]])
    
    # Assign default case for z value
    else:
        transform_matrix = np.array([[math.cos(angle), -math.sin(angle), 0], [math.sin(angle), math.cos(angle), 0], [0, 0, 1]])

    # Apply rotation matrix to each point
    for i, p in enumerate(stroke.points):
        p.co = transform_matrix @ np.array(p.co).reshape(3, 1)

#draws multiple circles at varying angles to create a sphere
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




# Animation Experiments
def animate_square_sliding(gp_layer):
  main_size = 4
  positions = np.linspace(-main_size / 2, main_size / 2, num=NUM_FRAMES)
  for frame in range(1, NUM_FRAMES):
      gp_frame = gp_layer.frames.new(frame*FRAMES_SPACING)
      _ = draw_square(gp_frame, (0, 0, 0), main_size)

      draw_square(gp_frame, (main_size/2+0.5, positions[frame], 0), 1)


def grid_animation(gp_layer):
    for frame in range(1, NUM_FRAMES):
        gp_frame = gp_layer.frames.new(frame)
        for i in range(15):
            #radius = np.random.randint(1, 7) + np.random.rand()
            squares_grid(gp_frame, 10, 10, rand_size=True, rand_rotation=False, material_index=1)
            
            
#single line animation        
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

    
    
    
    
   
    
