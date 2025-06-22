
import math
import random

from solar_objects import SpaceObject, Star, Planet, Satellite


gravitational_constant = 6.67408E-11


class SolarSystemModel:
    def __init__(self):
        self.space_objects = []
        self.physical_time = 0
        self.scale_factor = None

    def calculate_force(self, body):
        body.Fx = body.Fy = 0
        for obj in self.space_objects:
            if body == obj:
                continue

            # For satellites, we only calculate force from their parent planet
            if body.type == 'satellite' and obj != body.parent_planet:
                continue

            dx = obj.x - body.x
            dy = obj.y - body.y
            r = (dx ** 2 + dy ** 2) ** 0.5

            min_distance = 1e9
            if r < min_distance:
                repulsion = gravitational_constant * body.m * obj.m / (min_distance ** 2) * 10
                body.Fx -= repulsion * dx / r
                body.Fy -= repulsion * dy / r
            else:
                force = gravitational_constant * body.m * obj.m / (r ** 2)
                body.Fx += force * dx / r
                body.Fy += force * dy / r

    def move_space_object(self, body, dt):
        if body.type not in ['planet', 'satellite']:
            return

        if body.type == 'planet':
            central_body = body.parent_star
            if not central_body:
                return

            dx = body.x - central_body.x
            dy = body.y - central_body.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            angular_velocity = (gravitational_constant * central_body.m / distance ** 3) ** 0.5
            if hasattr(body, 'clockwise'):
                angular_velocity *= -1 if body.clockwise else 1

            angle = math.atan2(dy, dx) + angular_velocity * dt
            body.x = central_body.x + distance * math.cos(angle)
            body.y = central_body.y + distance * math.sin(angle)

        elif body.type == 'satellite':
            planet = body.parent_planet
            if not planet:
                return

            dx = body.x - planet.x
            dy = body.y - planet.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            orbital_speed = (gravitational_constant * planet.m / distance) ** 0.5

            current_angle = math.atan2(dy, dx)
            angular_velocity = orbital_speed / distance
            new_angle = current_angle + angular_velocity * dt

            body.x = planet.x + distance * math.cos(new_angle)
            body.y = planet.y + distance * math.sin(new_angle)

    def recalculate_positions(self, dt):
        for obj in self.space_objects:
            if obj.type == 'planet':
                direction = -1 if obj.clockwise else 1
                obj.orbit_angle += direction * obj.orbit_speed * dt

                sx = obj.parent_star.x
                sy = obj.parent_star.y
                r = obj.orbit_radius

                obj.x = sx + r * math.cos(obj.orbit_angle)
                obj.y = sy + r * math.sin(obj.orbit_angle)

                linear_speed = obj.orbit_speed * r
                obj.Vx = direction * linear_speed * -math.sin(obj.orbit_angle)
                obj.Vy = direction * linear_speed * math.cos(obj.orbit_angle)

            elif obj.type == 'satellite':
                direction = -1 if obj.clockwise else 1
                obj.orbit_angle += direction * obj.orbit_speed * dt

                px = obj.parent_planet.x
                py = obj.parent_planet.y
                r = obj.orbit_radius

                obj.x = px + r * math.cos(obj.orbit_angle)
                obj.y = py + r * math.sin(obj.orbit_angle)

                linear_speed = obj.orbit_speed * r
                obj.Vx = obj.parent_planet.Vx - direction * linear_speed * math.sin(obj.orbit_angle)
                obj.Vy = obj.parent_planet.Vy + direction * linear_speed * math.cos(obj.orbit_angle)

            else:
                obj.x += obj.Vx * dt
                obj.y += obj.Vy * dt
        self.check_collisions()

    def check_collisions(self):
        for i, obj1 in enumerate(self.space_objects):
            for obj2 in self.space_objects[i + 1:]:
                if self.objects_collide(obj1, obj2):
                    self.resolve_collision(obj1, obj2)

    def resolve_collision(self, obj1, obj2):
        dx = obj1.x - obj2.x
        dy = obj1.y - obj2.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        min_distance = (obj1.R + obj2.R) * 1e9 * 1.1

        if distance < 1e-9:
            angle = random.uniform(0, 2 * math.pi)
            dx = math.cos(angle)
            dy = math.sin(angle)
            distance = 1e-9

        correction = (min_distance - distance) / 2
        correction_x = correction * dx / distance
        correction_y = correction * dy / distance

        if obj1.type != 'star':
            obj1.x += correction_x
            obj1.y += correction_y
        if obj2.type != 'star':
            obj2.x -= correction_x
            obj2.y -= correction_y

    def objects_collide(self, obj1, obj2):
        min_distance = (obj1.R + obj2.R) * 1e9
        dx = obj1.x - obj2.x
        dy = obj1.y - obj2.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance < min_distance