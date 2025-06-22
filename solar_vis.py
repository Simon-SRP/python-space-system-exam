
import tkinter
from solar_objects import Star

window_width = 800
window_height = 800
header_font = "Arial-16"


class SolarSystemView:
    def __init__(self, root, model):
        self.model = model
        self.space = tkinter.Canvas(root, width=window_width, height=700, bg="black")
        self.space.pack(side=tkinter.TOP)
        self.show_orbits = True

        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.space.bind("<ButtonPress-1>", self.start_drag)
        self.space.bind("<B1-Motion>", self.drag)
        self.space.bind("<MouseWheel>", self.zoom)

        control_frame = tkinter.Frame(root)
        control_frame.pack(side=tkinter.BOTTOM)

        zoom_in_btn = tkinter.Button(control_frame, text="+", command=lambda: self.zoom(1.2))
        zoom_in_btn.pack(side=tkinter.LEFT)

        zoom_out_btn = tkinter.Button(control_frame, text="-", command=lambda: self.zoom(0.8))
        zoom_out_btn.pack(side=tkinter.LEFT)

        reset_btn = tkinter.Button(control_frame, text="Reset View", command=self.reset_view)
        reset_btn.pack(side=tkinter.LEFT)

    def scale_x(self, x):
        return int((x * self.model.scale_factor + self.offset_x) * self.scale) + window_width // 2

    def scale_y(self, y):
        return int((-y * self.model.scale_factor + self.offset_y) * self.scale) + window_height // 2

    def create_star_image(self, star):
        x = self.scale_x(star.x)
        y = self.scale_y(star.y)
        r = max(1, int(star.R * self.scale))
        star.image = self.space.create_oval([x - r, y - r], [x + r, y + r], fill=star.color)

    def create_planet_image(self, planet):
        x = self.scale_x(planet.x)
        y = self.scale_y(planet.y)
        r = max(1, int(planet.R * self.scale))
        planet.image = self.space.create_oval([x - r, y - r], [x + r, y + r], fill=planet.color)

    def update_system_name(self, system_name):
        self.space.delete("header")
        self.space.create_text(30, 30, tag="header", text=system_name, font=header_font, anchor="nw")

    def update_object_position(self, body):
        x = self.scale_x(body.x)
        y = self.scale_y(body.y)
        r = max(1, int(body.R * self.scale))

        if x + r < 0 or x - r > window_width or y + r < 0 or y - r > window_height:
            self.space.coords(body.image,
                              window_width + r,
                              window_height + r,
                              window_width + 2 * r,
                              window_height + 2 * r)
        else:
            self.space.coords(body.image, x - r, y - r, x + r, y + r)

    def draw_orbits(self):
        self.space.delete("orbit")
        stars = [obj for obj in self.model.space_objects if obj.type == 'star']

        for star in stars:
            planets = [obj for obj in self.model.space_objects if
                       hasattr(obj, 'parent_star') and obj.parent_star == star]
            unique_orbits = set()

            for planet in planets:
                if hasattr(planet, 'orbit_radius') and planet.orbit_radius not in unique_orbits:
                    unique_orbits.add(planet.orbit_radius)
                    x = self.scale_x(star.x)
                    y = self.scale_y(star.y)
                    radius = planet.orbit_radius * self.model.scale_factor * self.scale
                    self.space.create_oval(x - radius, y - radius, x + radius, y + radius,
                                           outline="gray", dash=(2, 2), tag="orbit")

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.offset_x -= dx / self.scale
        self.offset_y -= dy / self.scale
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.redraw_all()

    def zoom(self, factor):
        if isinstance(factor, tkinter.Event):
            delta = factor.delta
            factor = 1.1 if delta > 0 else 0.9

        mouse_x = factor.x if isinstance(factor, tkinter.Event) else window_width / 2
        mouse_y = factor.y if isinstance(factor, tkinter.Event) else window_height / 2

        old_scale = self.scale
        self.scale *= factor
        self.scale = max(0.1, min(10.0, self.scale))

        self.offset_x += (mouse_x - window_width / 2) * (1 / old_scale - 1 / self.scale)
        self.offset_y += (mouse_y - window_height / 2) * (1 / old_scale - 1 / self.scale)

        self.redraw_all()

    def reset_view(self):
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.redraw_all()

    def redraw_all(self):
        self.space.delete("all")
        for body in self.model.space_objects:
            if body.type == 'star':
                self.create_star_image(body)
            else:
                self.create_planet_image(body)

        if self.show_orbits:
            self.draw_orbits()