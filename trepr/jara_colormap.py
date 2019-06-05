from colour import Color
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap

left = Color(rgb=(102/255, 0/255, 204/255))
middle = Color(rgb=(1, 1, 1))
right = Color(rgb=(255/255, 51/255, 51/255))

R_left = np.linspace(102 / 255, 1, 128)
G_left = np.linspace(0, 1, 128)
B_left = np.linspace(204 / 255, 1, 128)

R_right = np.linspace(1, 255/255, 128)
G_right = np.linspace(1, 51/255, 128)
B_right = np.linspace(1, 51/255, 128)

colors_left = list(left.range_to(middle, 128))
colors_right = list(middle.range_to(right, 128))
for i in range(len(colors_left)):
    colors_left[i] = list(colors_left[i].rgb)
for i in range(len(colors_right)):
    colors_right[i] = list(colors_right[i].rgb)

for i in range(len(colors_left)):
    colors_left[i][0] = R_left[i]
    colors_left[i][1] = G_left[i]
    colors_left[i][2] = B_left[i]

for i in range(len(colors_right)):
    colors_right[i][0] = R_right[i]
    colors_right[i][1] = G_right[i]
    colors_right[i][2] = B_right[i]

viridis = cm.get_cmap('viridis', 256)
jara_colors = viridis(np.linspace(0,1,256))

for i in range(0, 127):
    jara_colors[i][0:3] = colors_left[i][0:3]
for i in range(128,255):
    jara_colors[i][0:3] = colors_right[i - 128][0:3]

jara_cmap = ListedColormap(jara_colors)
