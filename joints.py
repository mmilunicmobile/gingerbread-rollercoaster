import vector as vec
import math

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
        self.flattancrossnorm = vec.obj(x = self.tangent.x, y = self.tangent.y, z = 0).cross(self.normal).unit()

    
    # def roll(self) -> float:
    #     return math.pi / 2 - self.angle.theta
    
    # def theta(self) -> float:
    #     return self.angle.phi
        
    def roll(self) -> float:
        initialAngle = self.flattancrossnorm.deltaangle(vec.obj(x = self.tangent.x, y = self.tangent.y, z = 0).rotateZ(-math.pi/2))
        return initialAngle if self.flattancrossnorm.theta < math.pi/2 else -initialAngle
    
    def theta(self) -> float:
        return self.tangent.rotateZ(-math.pi/2).phi
    
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