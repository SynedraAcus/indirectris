"""
A gravity system and basic attractor/attractee/gravfield classes
"""

from bear_hug.widgets import Widget
from collections import namedtuple
from math import sqrt

Gravcell = namedtuple('Gravcell', ('ax', 'ay'))

class GravityField:
    """
    A gravity field that contains multiple attractors
    """
    def __init__(self, size):
        """
        
        :param size: tuple of ints (xsize, ysize)
        """
        self.size = size
        self.sum_field = [[Gravcell(0, 0) for y in range(size[1])]
                          for x in range(size[0])]
        self.attractor_fields = {}
        self.positions = {}
        
    def add_attractor(self, attractor, pos):
        """
        Add an attractor
        :param attractor:
        :return:
        """
        assert isinstance(attractor, Attractor)
        self.positions[attractor] = pos
        self.attractor_fields[attractor] = [[Gravcell(0, 0)
                                             for y in range(self.size[1])]
                                            for x in range(self.size[0])]
        self.rebuild_attractor_field(attractor)
        self.rebuild_sum_field()
    
    def rebuild_attractor_field(self, attractor):
        """
        Rebuild the attractor's field
        :param attractor:
        :return:
        """
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                dist = sqrt((x - self.positions[attractor][0])**2 + (y - self.positions[attractor][1])**2)
                if self.positions[attractor][0] != x:
                    a_x = attractor.mass * abs(x - self.positions[attractor][0]) / dist ** 3
                    if self.positions[attractor][0] <= x:
                        a_x *= -1
                else:
                    a_x = 0
                if self.positions[attractor][1] != y:
                    a_y = attractor.mass * abs(y - self.positions[attractor][1]) / dist ** 3
                    if self.positions[attractor][1] <= y:
                        a_y *= -1
                else:
                    a_y = 0
                self.attractor_fields[attractor][x][y] = Gravcell(a_x, a_y)
            
    def rebuild_sum_field(self):
        """
        Rebuild sum field as a sum of attractor fields
        :return:
        """
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                a_x = sum(self.attractor_fields[a][x][y].ax
                            for a in self.attractor_fields)
                a_y = sum(self.attractor_fields[a][x][y].ay
                            for a in self.attractor_fields)
                self.sum_field[x][y] = Gravcell(a_x, a_y)
        for y in range(self.size[1]):
            print(';'.join(f'{x.ax}, {x.ay}' for x in self.sum_field[y]))
    
    def __getitem__(self, item):
        # List API for ease of lookup
        return self.sum_field[item]

        
class Attractor(Widget):
    def __init__(self, *args, mass=100, field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mass = mass
        self.field = field
        # Easier to remember position here
        
    def on_event(self, event):
        pass
    

class Attractee(Widget):
    def __init__(self, *args, field=None, vx=1, vy=1, attr = None,**kwargs):
        super().__init__(*args, **kwargs)
        self.field = field
        # Easier to remember position here
        self.vx = vx
        self.vy = vy
        # Delay between steps, in seconds
        if self.vx != 0:
            self.x_delay = abs(1/self.vx)
        else:
            self.x_delay = 0
        if self.vy != 0:
            self.y_delay = abs(1/self.vy)
        else:
            self.y_delay = 0
        # How long since last step
        self.x_waited = 0
        self.y_waited = 0
        self.attr = attr
        
    # def on_event(self, event):
    #     if event.event_type == 'tick':
    #         x, y = self.parent.widget_locations[self].pos
    #         attr_x, attr_y = self.parent.widget_locations[self.attr].pos
    #         dist = sqrt((x - attr_x) ** 2 + (y - attr_y) ** 2)
    #         self.vx += (self.attr.mass * (attr_x - x) / dist ** 3) * event.event_value
    #         self.vy += (self.attr.mass * (attr_y - y) / dist ** 3) * event.event_value
    #         self.x_delay = abs(1/self.vx)
    #         self.y_delay = abs(1/self.vy)
    #         self.x_waited += event.event_value
    #         self.y_waited += event.event_value
    #         print(self.vx, self.vy)
    #         if self.x_waited >= self.x_delay and self.vx != 0):
    #             self.parent.move_widget(self, (x+round(self.vx/abs(self.vx)),
    #                                            y), refresh=True)
    #             self.x_waited = 0
    #         if self.y_waited >= self.y_delay and self.vy != 0:
    #             self.parent.move_widget(self, (x, y+round(self.vy/abs(self.vy))),
    #                                     refresh=True)
    #             self.y_waited = 0
        
    def on_event(self, event):
        if event.event_type == 'tick':
            self.x_waited += event.event_value
            self.y_waited += event.event_value
            xpos, ypos = self.parent.widget_locations[self].pos
            self.vx += self.field[xpos][ypos].ax * event.event_value
            self.vy += self.field[xpos][ypos].ay * event.event_value
            print(self.vx, self.vy)
            if self.vx != 0:
                self.x_delay = abs(1 / self.vx)
            if self.vy != 0:
                self.y_delay = abs(1 / self.vy)
            if self.x_waited >= self.x_delay and self.vx != 0:
                new_x = xpos+round(self.vx/abs(self.vx))
                # self.parent.move_widget(self, (xpos+round(self.vx/abs(self.vx)),
                #                                ypos), refresh=True)
                self.x_waited = 0
            else:
                new_x = xpos
            if self.y_waited >= self.y_delay and self.vy != 0:
                new_y = ypos+round(self.vy/abs(self.vy))
                # self.parent.move_widget(self, (xpos,
                #                                ypos+round(self.vy/abs(self.vy))),
                #                         refresh=True)
                self.y_waited = 0
            else:
                new_y = ypos
            self.parent.move_widget(self, (new_x, new_y), refresh=True)

    #
