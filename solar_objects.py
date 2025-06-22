
class SpaceObject:
    def __init__(self, obj_type, x=0, y=0, Vx=0, Vy=0, m=0, R=5, color="red"):
        self.type = obj_type
        self.x = x
        self.y = y
        self.Vx = Vx
        self.Vy = Vy
        self.Fx = 0
        self.Fy = 0
        self.m = m
        self.R = R
        self.color = color
        self.image = None


class Star(SpaceObject):
    def __init__(self, x=0, y=0, Vx=0, Vy=0, m=0, R=5, color="red"):
        super().__init__("star", x, y, Vx, Vy, m, R, color)


class Planet(SpaceObject):
    def __init__(self, x=0, y=0, Vx=0, Vy=0, m=0, R=5, color="green"):
        super().__init__("planet", x, y, Vx, Vy, m, R, color)
        self.parent_star = None
        self.orbit_radius = 0
        self.orbit_speed = 0
        self.clockwise = True
        self.satellites = []
        self.orbit_angle = 0.0


class Satellite(SpaceObject):
    def __init__(self, x=0, y=0, Vx=0, Vy=0, m=0, R=2, color="red"):
        super().__init__("satellite", x, y, Vx, Vy, m, R, color)
        self.parent_planet = None
        self.clockwise = True
        self.orbit_radius = 0
        self.orbit_angle = 0.0
        self.orbit_speed = 0.0  # Угловая скорость (радиан/с)
