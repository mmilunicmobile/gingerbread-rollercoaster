from typing import List
import vector as vec
import csv
import math
import colorsys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from joints import *

import createtrack

coords = []

"""
The size of the house is:
 x: 1.86 * height (22.32 in) 2.36
 y: 3.68 * height (44.16) 4.18
 z: height
"""
x_size = 2.36
y_size = 4.18

rail_spacing = 1/3/12

scale_constant = 46.0133857727051
    
offsetConstant = vec.obj(x=.9581111400446335 + 3/12, y= 1.8970500491082292 + 3/12, z=0)

with open('data.csv', newline='') as csvfile:
    first_coords = []

    reader = csv.DictReader(csvfile)
    for row in reader:
        first_coords.append(row)
    
    for i in range(-1, len(first_coords) - 1):
        row = first_coords[i]
        rowNext = first_coords[i+1]
        rowLast = first_coords[i-1]
        coords.append(Joint(
            vec.obj(x=float(row['x']),y=float(row['y']),z=float(row['z'])) / scale_constant + offsetConstant,
            vec.obj(x=float(rowLast['ax']),y=float(rowLast['ay']),z=float(rowLast['az'])) / scale_constant + offsetConstant,
            vec.obj(x=float(rowNext['x']),y=float(rowNext['y']),z=float(rowNext['z'])) / scale_constant + offsetConstant,
            row['id']))

def a_b_listinator(lambdaThingy):
    return [lambdaThingy(coords[i-1], coords[i]) for i in range(0, len(coords))]

runningLength = 0

segmentLength = 2/12

current_index = 0

supportsIndexes = []

while (current_index < len(coords)):
    supportsIndexes.append(current_index)
    while (runningLength < segmentLength):
        current_index += 1
        if current_index >= len(coords):
            break
        # print(current_index)
        runningLength += (coords[current_index - 1].groundCoordinate(0) - coords[current_index].groundCoordinate(0)).rho
    runningLength -= segmentLength

my_supports = list(map(lambda i: PersonalJoint.customConstructor(coords[i]), supportsIndexes))

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def convert(*value):
    return tuple(map(lambda e: int(e * 12 * 150), value))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

coasterCoordsMatpltLeft = [[],[],[]]
coasterCoordsMatpltRight = [[],[],[]]

from PIL import Image, ImageDraw, ImageFont
im = Image.new('RGBA', convert(x_size, y_size), (255, 255, 255, 255)) 
draw = ImageDraw.Draw(im) 
for i in range(0, len(coords)):
    draw.line(convert(coords[i-1].main.x, y_size - coords[i-1].main.y, coords[i].main.x, y_size - coords[i].main.y), fill = (0,0,0,255), width= 9)

for i in coords:
    poseRight = i.railCoordinate(rail_spacing)
    poseLeft = i.railCoordinate(-rail_spacing)
    coasterCoordsMatpltRight[0].append(poseRight.x)
    coasterCoordsMatpltRight[1].append(poseRight.y)
    coasterCoordsMatpltRight[2].append(poseRight.z)
    coasterCoordsMatpltLeft[0].append(poseLeft.x)
    coasterCoordsMatpltLeft[1].append(poseLeft.y)
    coasterCoordsMatpltLeft[2].append(poseLeft.z)

ax.set_xlim([0, 5])
ax.set_ylim([0, 5])
ax.set_zlim([0, 5])

for num, i in enumerate(my_supports):
    draw.line(convert(
        1/12 * math.cos(i.angle) + i.x, y_size - (1/12 * math.sin(i.angle) + i.y),
        -1/12 * math.cos(i.angle) + i.x, y_size - (-1/12 * math.sin(i.angle) + i.y)
        ), fill=(*hsv2rgb(num/len(my_supports),1,1),255), width = 9)
    ax.plot(
        [1/12 * math.cos(i.angle) * math.cos(i.roll) + i.x, -1/12 * math.cos(i.angle) * math.cos(i.roll) + i.x],
        [1/12 * math.sin(i.angle) * math.cos(i.roll) + i.y, -1/12 * math.sin(i.angle) * math.cos(i.roll) + i.y],
        [1/12 * math.sin(i.roll) + i.z, -1/12 * math.sin(i.roll) + i.z],
        color="black")
    
ax.plot(*coasterCoordsMatpltLeft, color="red")
ax.plot(*coasterCoordsMatpltRight, color="red")

font = ImageFont.truetype("Arial.ttf", 16 * 3)

for num, i in enumerate(my_supports):
    draw.text(convert(i.x, y_size - i.y),f"S#{num}",(0,0,0, 255),font=font)


file_path = "output.txt"

# Open the file in write mode ('w')
with open(file_path, 'w') as file:
    # Write content to the file
    for num, i in enumerate(my_supports):
        file.write(f"S#{num}: {i.essential()}\n")

print(f"Content has been written to {file_path}")


def createTrackAndImages(rail_position, name_modifier, name_abbreviation, color):
    runningLength = 0

    segmentLength = 7/12

    current_index = 0

    leftTrackIndexes = []

    while (current_index < len(coords)):
        leftTrackIndexes.append(current_index)
        while (runningLength < segmentLength):
            current_index += 1
            if current_index >= len(coords):
                break
            # print(current_index)
            runningLength += (coords[current_index - 1].railCoordinate(rail_position) - coords[current_index].railCoordinate(rail_position)).mag
        runningLength -= segmentLength

    for i in range(0, len(leftTrackIndexes) - 1):
        createtrack.drawCoords(createtrack.transformTrackSection(list(map(lambda e: e.railCoordinate(rail_position), coords[leftTrackIndexes[i]:leftTrackIndexes[i+1]]))), f"{i}{name_modifier}")
        draw.text(convert(coords[leftTrackIndexes[i]].railCoordinate(rail_position).x, y_size - coords[leftTrackIndexes[i]].railCoordinate(rail_position).y),f"T#{i}{name_abbreviation}",color,font=font)
        draw.line(convert(
            coords[leftTrackIndexes[i]].railCoordinate(rail_position).x, y_size - coords[leftTrackIndexes[i]].railCoordinate(rail_position).y,
            coords[leftTrackIndexes[i]].railCoordinate(-0).x, y_size - coords[leftTrackIndexes[i]].railCoordinate(-0).y
            ), fill=color, width = 9)
    createtrack.drawCoords(createtrack.transformTrackSection(list(map(lambda e: e.railCoordinate(rail_position), coords[leftTrackIndexes[-1]:]))), f"{len(leftTrackIndexes) - 1}{name_modifier}")
    draw.text(convert(coords[leftTrackIndexes[-1]].railCoordinate(rail_position).x, y_size - coords[leftTrackIndexes[-1]].railCoordinate(rail_position).y),f"T#{len(leftTrackIndexes) - 1}{name_abbreviation}",color,font=font)
    draw.line(convert(
            coords[leftTrackIndexes[i]].railCoordinate(rail_position).x, y_size - coords[leftTrackIndexes[i]].railCoordinate(rail_position).y,
            coords[leftTrackIndexes[i]].railCoordinate(-0).x, y_size - coords[leftTrackIndexes[i]].railCoordinate(-0).y
            ), fill=color, width = 9)

createTrackAndImages(
    -rail_spacing, "left", "L", (255,0,0,255)
)

createTrackAndImages(
    rail_spacing, "right", "R", (0,0,255,255)
)

#im.show()

im.save("myOutput.png", dpi=convert(1/12,1/12))

# plt.show()