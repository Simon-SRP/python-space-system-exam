import tkinter
from tkinter.filedialog import *
from tkinter import messagebox
from solar_model import SolarSystemModel, gravitational_constant
from solar_objects import Star, Planet, Satellite
from solar_vis import SolarSystemView, window_width, window_height
import math
import random


perform_execution = False
model = SolarSystemModel()
view = None
root = None
start_button = None
time_step = None
displayed_time = None


def main():
    global root, view, start_button, time_step, displayed_time

    root = tkinter.Tk()
    time_step = tkinter.DoubleVar(root)
    displayed_time = tkinter.StringVar(root)
    time_step.set(100000)
    displayed_time.set("0.0 seconds gone")

    view = SolarSystemView(root, model)
    create_ui(root)
    root.mainloop()


def create_ui(root):
    global start_button

    frame = tkinter.Frame(root)
    frame.pack(side=tkinter.BOTTOM)

    start_button = tkinter.Button(frame, text="Start", command=start_execution, width=6)
    start_button.pack(side=tkinter.LEFT)

    time_step_entry = tkinter.Entry(frame, textvariable=time_step)
    time_step_entry.pack(side=tkinter.LEFT)

    load_button = tkinter.Button(frame, text="Open File", command=open_file_dialog)
    load_button.pack(side=tkinter.LEFT)



    save_button = tkinter.Button(frame, text="Save to file", command=save_file_dialog)
    save_button.pack(side=tkinter.LEFT)

    orbit_button = tkinter.Button(frame, text="Toggle Orbits", command=toggle_orbits)
    orbit_button.pack(side=tkinter.LEFT)

    time_label = tkinter.Label(frame, textvariable=displayed_time, width=30)
    time_label.pack(side=tkinter.RIGHT)


def execution():
    global perform_execution, model, view

    if not perform_execution:
        return

    view.space.delete("all")
    model.recalculate_positions(time_step.get())

    for body in model.space_objects:
        if body.type == 'star':
            view.create_star_image(body)
        else:
            view.create_planet_image(body)

    if view.show_orbits:
        view.draw_orbits()

    displayed_time.set(f"{model.physical_time:.1f} seconds gone")
    view.space.update_idletasks()
    view.space.update()
    view.space.after(50, execution)


def start_execution():
    global perform_execution, start_button

    perform_execution = True
    start_button['text'] = "Pause"
    start_button['command'] = stop_execution
    execution()


def stop_execution():
    global perform_execution, start_button

    perform_execution = False
    start_button['text'] = "Start"
    start_button['command'] = start_execution


def generate_solar_system():
    global model

    model.space_objects = []
    create_stars()
    create_planets_for_star(model.space_objects[0], 16, [8, 10, 13])
    create_planets_for_star(model.space_objects[1], 20, [10, 15, 20])
    set_scale_factor()
    return model.space_objects


def create_stars():
    global model

    star1 = create_star(-200e9, 0, "yellow", 1.98892E30, 20)
    star2 = create_star(200e9, 0, "orange", 1.98892E30 * 1.2, 18)
    model.space_objects.extend([star1, star2])


def create_star(x, y, color, mass, radius):
    star = Star(x, y, color=color)
    star.m = mass
    star.R = radius
    return star


def create_planets_for_star(star, count, satellites_at):
    global model

    for i in range(1, count + 1):
        planet = create_planet_for_star(star, i)
        model.space_objects.append(planet)

        if i in satellites_at:
            satellite = create_satellite_for_planet(planet)
            model.space_objects.append(satellite)


def create_planet_for_star(star, planet_number):
    planet = Planet()
    planet.parent_star = star
    planet.orbit_radius = 30e9 + planet_number * (15e9 if planet.parent_star == model.space_objects[0] else 10e9)
    planet.orbit_angle = random.uniform(0, 2 * math.pi)

    planet.x = star.x + planet.orbit_radius * math.cos(planet.orbit_angle)
    planet.y = star.y + planet.orbit_radius * math.sin(planet.orbit_angle)

    planet.clockwise = (planet_number % 2) == 0
    speed = (gravitational_constant * star.m / planet.orbit_radius) ** 0.5

    if planet.clockwise:
        planet.Vx = speed * math.sin(planet.orbit_angle)
        planet.Vy = -speed * math.cos(planet.orbit_angle)
    else:
        planet.Vx = -speed * math.sin(planet.orbit_angle)
        planet.Vy = speed * math.cos(planet.orbit_angle)

    planet.orbit_speed = speed / planet.orbit_radius
    planet.m = random.uniform(1e24, 1e25)
    planet.color = generate_random_color()
    planet.R = random.randint(5, 10)
    return planet


def create_satellite_for_planet(planet):
    satellite = Satellite()
    satellite.parent_planet = planet
    satellite.orbit_radius = planet.R * 1.5e9
    sat_angle = random.uniform(0, 2 * math.pi)

    satellite.x = planet.x + satellite.orbit_radius * math.cos(sat_angle)
    satellite.y = planet.y + satellite.orbit_radius * math.sin(sat_angle)

    sat_speed = (gravitational_constant * planet.m / satellite.orbit_radius) ** 0.5
    satellite.Vx = planet.Vx - sat_speed * math.sin(sat_angle)
    satellite.Vy = planet.Vy + sat_speed * math.cos(sat_angle)

    satellite.orbit_angle = sat_angle
    satellite.orbit_speed = sat_speed / satellite.orbit_radius
    satellite.clockwise = True
    satellite.m = planet.m * 0.001
    satellite.color = "gray"
    satellite.R = planet.R * 0.4
    return satellite


def generate_random_color():
    return f"#{random.randint(50, 200):02x}{random.randint(50, 200):02x}{random.randint(50, 200):02x}"


def set_scale_factor():
    global model

    max_distance = max(max(abs(obj.x), abs(obj.y)) for obj in model.space_objects)
    model.scale_factor = 0.4 * min(window_height, window_width) / max_distance


def open_file_dialog():
    global perform_execution

    perform_execution = False
    filename = askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))

    if filename:
        success = load_from_file(filename)
        if success:
            display_system()
            view.update_system_name("Loaded from: " + filename)
        else:
            messagebox.showerror("Error", "Failed to load the file")


def display_system():
    global model, view

    view.space.delete("all")
    for obj in model.space_objects:
        if obj.type == 'star':
            view.create_star_image(obj)
        elif obj.type in ['planet', 'satellite']:
            view.create_planet_image(obj)

    if view.show_orbits:
        view.draw_orbits()


def save_file_dialog():
    out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
    if out_filename:
        write_space_objects_data_to_file(out_filename)


def load_from_file(filename):
    global model

    model.space_objects = []
    object_types = {'Star': Star, 'Planet': Planet, 'Satellite': Satellite}

    try:
        with open(filename, 'r') as f:
            for line in f:
                if not line.strip():
                    continue

                parts = line.split()
                obj_type = parts[0]
                if obj_type not in object_types:
                    continue

                obj = create_object_from_line(parts, object_types[obj_type])
                if obj:
                    model.space_objects.append(obj)

        set_scale_factor()
        return True

    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return False


def create_object_from_line(parts, obj_class):
    obj = obj_class()
    obj.R = float(parts[1])
    obj.color = parts[2]
    obj.m = float(parts[3])
    obj.x = float(parts[4])
    obj.y = float(parts[5])
    obj.Vx = float(parts[6])
    obj.Vy = float(parts[7])

    # For planets and satellites set parent objects
    if obj_class == Planet:
        # Find nearest star as parent
        min_dist = float('inf')
        for potential_parent in model.space_objects:
            if potential_parent.type == 'star':
                dist = ((obj.x - potential_parent.x) ** 2 +
                        (obj.y - potential_parent.y) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    obj.parent_star = potential_parent

        # Set orbital parameters
        if obj.parent_star:
            dx = obj.x - obj.parent_star.x
            dy = obj.y - obj.parent_star.y
            obj.orbit_radius = (dx ** 2 + dy ** 2) ** 0.5
            obj.orbit_angle = math.atan2(dy, dx)

            # Calculate angular velocity
            velocity_tangent = (-obj.Vx * dy + obj.Vy * dx) / obj.orbit_radius
            obj.orbit_speed = velocity_tangent / obj.orbit_radius
            obj.clockwise = velocity_tangent > 0

    elif obj_class == Satellite:
        # Find nearest planet as parent
        min_dist = float('inf')
        for potential_parent in model.space_objects:
            if potential_parent.type == 'planet':
                dist = ((obj.x - potential_parent.x) ** 2 +
                        (obj.y - potential_parent.y) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    obj.parent_planet = potential_parent

        # Set orbital parameters
        if obj.parent_planet:
            dx = obj.x - obj.parent_planet.x
            dy = obj.y - obj.parent_planet.y
            obj.orbit_radius = (dx ** 2 + dy ** 2) ** 0.5
            obj.orbit_angle = math.atan2(dy, dx)

            # Calculate angular velocity
            velocity_tangent = (-obj.Vx * dy + obj.Vy * dx) / obj.orbit_radius
            obj.orbit_speed = velocity_tangent / obj.orbit_radius
            obj.clockwise = velocity_tangent > 0

    return obj


def write_space_objects_data_to_file(output_filename):
    global model

    with open(f'{output_filename}.txt', 'w') as out_file:
        for obj in model.space_objects:
            if isinstance(obj, Star):
                obj_type = "Star"
            elif isinstance(obj, Planet):
                obj_type = "Planet"
            elif isinstance(obj, Satellite):
                obj_type = "Satellite"
            else:
                continue

            out_file.write(
                f"{obj_type} {obj.R} {obj.color} {obj.m} {obj.x} {obj.y} {obj.Vx} {obj.Vy}\n"
            )


def toggle_orbits():
    global view

    view.show_orbits = not view.show_orbits
    if not view.show_orbits:
        view.space.delete("orbit")
    else:
        view.draw_orbits()


if __name__ == "__main__":
    main()