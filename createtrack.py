from PIL import Image, ImageDraw, ImageFont
from typing import List
from joints import *
import numpy as np
from scipy.spatial.distance import cdist

def convert(*value):
    return tuple(map(lambda e: int(e * 12 * 150), value))

font = ImageFont.truetype("Arial.ttf", 16 * 2)

def transformTrackSection(coords: List[vec.Vector3D]):
    points = np.array(list(map(lambda e: [e.x, e.y, e.z], [
        coords[0], 
        coords[len(coords)//3 - 1], 
        coords[2 * len(coords)//3 - 1], 
        coords[-1]
        ])))
    (x_norm, y_norm, z_norm), distance_to_origin = plane_of_best_fit(points)
    normal_vector = vec.obj(x=x_norm, y=y_norm, z=z_norm)

    new_coords = [i.rotateZ(-normal_vector.phi).rotateY(-normal_vector.theta) for i in coords]
    
    min_height = min([coord.z for coord in new_coords])
    min_x = min([coord.x for coord in new_coords])
    min_y = min([coord.y for coord in new_coords])

    newer_coords = [i + vec.obj(x=-min_x + .5/12,y=-min_y + .5/12,z=-min_height + .5/12) for i in new_coords]

    return newer_coords

def drawCoords(coords: List[vec.Vector3D], id: str):
    drawCoordsBase(coords, id)
    drawCoordsHeight(coords, id)

def drawCoordsHeight(coords, id):
    to_flat = lambda e: vec.obj(x=e.x, y=e.y, z=0)
    length = sum([to_flat(coords[i + 1] - coords[i]).mag for i in range(0, len(coords) - 1)])
    max_x = max([coord.z for coord in coords]) + 1/12
    max_y = length + 1/12

    im = Image.new('RGBA', convert(max_x, max_y), (255, 255, 255, 0)) 
    draw = ImageDraw.Draw(im) 

    properCoords = []

    runningLength = .5/12

    for i in range(0, len(coords) -1):
        properCoords.append(.5/12 + coords[i].z)
        properCoords.append(runningLength)
        runningLength += to_flat(coords[i+1] - coords[i]).mag
    
    properCoords.append(.5/12 + coords[-1].z)
    properCoords.append(.5/12 + length)
    
    properCoords.append(.5/12)
    properCoords.append(.5/12 + length)

    properCoords.append(.5/12)
    properCoords.append(.5/12)

    properCoords.append(.5/12 + coords[0].z)
    properCoords.append(.5/12)

    draw.line(convert(*properCoords), fill=(0,0,0,255), width = 6)

    draw.text(convert(0, 0),f"T#{id}_height",(0,0,0, 255),font=font)
    draw.text(convert(.5/12, .5/12),f"{id}",(0,255,0, 255),font=font)

    im.save(f"TwizzlerMoldsHeights/T#{id}_height.png", dpi=convert(1/12,1/12))


def drawCoordsBase(coords, id):
    max_x = max([coord.x for coord in coords]) + .5/12
    max_y = max([coord.y for coord in coords]) + .5/12

    im = Image.new('RGBA', convert(max_x, max_y), (255, 255, 255, 0)) 
    draw = ImageDraw.Draw(im) 

    properCoords = []

    for i in coords:
        properCoords.append(i.x)
        properCoords.append(max_y - i.y)
    
    draw.line(convert(*properCoords), fill=(0,0,0,255), width = 6)

    #draw.text(convert(0, 0),f"T#{id}",(0,0,0, 255),font=font)
    draw.text(convert(properCoords[0], properCoords[1]),f"T#{id}",(0,255,0, 255),font=font)

    im.save(f"TwizzlerMoldsBases/T#{id}.png", dpi=convert(1/12,1/12))

def plane_of_best_fit(points):
    """Finds the plane of best fit for a set of points.

    Args:
        points: A NumPy array of points, where each point is a 3D coordinate.

    Returns:
        A tuple of (a, b, c, d), where (a, b, c) is the normal vector to the plane and
        d is the distance from the origin to the plane.
    """

    # Compute the covariance matrix of the points.
    covariance = np.cov(points, rowvar=False)

    # Compute the eigenvalues and eigenvectors of the covariance matrix.
    eigenvalues, eigenvectors = np.linalg.eig(covariance)

    # The normal vector to the plane is the eigenvector corresponding to the smallest
    # eigenvalue.
    normal_vector = eigenvectors[:, np.argmin(eigenvalues)]

    # The distance from the origin to the plane is the negative of the dot product
    # of the normal vector and the mean of the points.
    distance_to_origin = -np.dot(normal_vector, np.mean(points, axis=0))

    return normal_vector, distance_to_origin