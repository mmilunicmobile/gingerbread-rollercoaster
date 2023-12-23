import vector as vec
import csv
import math
import colorsys


coords = []

class Joint:
    def __init__(self, main: vec.Vector3D, angle: vec.Vector3D, nextMain: vec.Vector3D, id: int) -> None:
        self.main = main
        self.unchanged_angle = angle
        self.unscaled_angle = (angle - main)
        self.angle = self.unscaled_angle.unit()
        self.unscaled_tangent = nextMain - main
        self.tangent = self.unscaled_tangent.unit()
        self.normal = self.angle.cross(self.tangent).unit()
        self.id = int(id)

    
    def roll(self) -> float:
        return math.pi / 2 - self.angle.theta
    
    def theta(self) -> float:
        return self.angle.phi
    
    def railCoordinate(self, offset: float) -> vec.Vector3D:
        return self.relativeCoordinate(offset, 0, 0)
    
    def supportCoordinate(self, verticalOffset: float) -> vec.Vector3D:
        return self.relativeCoordinate(0, -verticalOffset, 0)
    
    def groundCoordinate(self, verticalOffset: float) -> vec.Vector2D:
        coordinate = self.supportCoordinate(verticalOffset)
        return vec.obj(x=coordinate.x, y=coordinate.y)
        
    def heightCoordinate(self, verticalOffset: float) -> float:
        return self.supportCoordinate(verticalOffset).z

    def relativeCoordinate(self, angle: float, normal: float, tangent: float) -> vec.Vector3D:
        """For this, normal is the normal of the track, tangent is the direction of the track, 
        and angle is to the right of the track as defined by tangent X normal."""
        return self.main + self.angle * angle + self.normal * normal + self.tangent * tangent
    
class PersonalJoint:
    def __init__(self, x: float, y: float, z:float, angle: float, roll: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.roll = roll
    
    @staticmethod
    def customConstructor(thingy: Joint) -> 'PersonalJoint':
        spot = thingy.supportCoordinate((1/8)/12)
        return PersonalJoint(spot.x, spot.y, spot.z, thingy.theta(), thingy.roll())
    
    def __str__(self):
        return f"({self.x*12:.1f} in, {self.y*12:.1f} in), Height: {self.z*12:.1f} in, Angle: {math.degrees(self.angle):.0f} deg, Roll: {math.degrees(self.roll):.0f} deg"
    
    def essential(self):
        return f"Height: {self.z*12:.1f} in, Roll: {math.degrees(self.roll):.0f} deg, Pose: ({self.x*12:.1f} in, {self.y*12:.1f} in), Angle: {math.degrees(self.angle):.0f} deg"

"""
The size of the house is:
 x: 1.86 * height (22.32 in) 2.36
 y: 3.68 * height (44.16) 4.18
 z: height
"""
x_size = 2.36
y_size = 4.18

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
    return tuple(map(lambda e: int(e * 12 * 50), value))


from PIL import Image, ImageDraw, ImageFont
im = Image.new('RGBA', convert(x_size, y_size), (255, 255, 255, 255)) 
draw = ImageDraw.Draw(im) 
for i in range(0, len(coords) -1):
    draw.line(convert(coords[i-1].main.x, y_size - coords[i-1].main.y, coords[i].main.x, y_size - coords[i].main.y), fill = (0,0,0,255), width= 3)

for num, i in enumerate(my_supports):
    draw.line(convert(
        1/12 * math.cos(i.angle) + i.x, y_size - (1/12 * math.sin(i.angle) + i.y),
        -1/12 * math.cos(i.angle) + i.x, y_size - (-1/12 * math.sin(i.angle) + i.y)
        ), fill=(*hsv2rgb(num/len(my_supports),1,1),255), width = 3)

font = ImageFont.truetype("Arial.ttf", 16)

for num, i in enumerate(my_supports):
    draw.text(convert(i.x, y_size - i.y),f"S#{num}",(0,0,0, 255),font=font)

im.show()

im.save("myOutput.png", dpi=convert(1/12,1/12))

file_path = "output.txt"

# Open the file in write mode ('w')
with open(file_path, 'w') as file:
    # Write content to the file
    for num, i in enumerate(my_supports):
        file.write(f"S#{num}: {i.essential()}\n")

print(f"Content has been written to {file_path}")

