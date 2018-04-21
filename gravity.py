"""
A gravity system and basic attractor/attractee/gravfield classes
"""

from bear_hug.bear_utilities import copy_shape
from bear_hug.event import BearEvent
from bear_hug.widgets import Widget, Listener
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
        
    def move_attractor(self, attractor, pos):
        self.positions[attractor] = pos
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
        print('Rebuilt')
    
    def __getitem__(self, item):
        # List API for ease of lookup
        return self.sum_field[item]


class TetrisSystem:
    """
    All the tetris logic
    
    Cell can contain either zero (can move), 1 (should stop and all the moved
    cells become 1) or 2 (should stop and moved element should be destroyed,
    eg with screen edges or attractor centers).
    2 takes precedence over 1
    """
    def __init__(self, size):
        self.size = size
        self.cells = [[0 for y in range(size[1])] for x in range(size[0])]
        for x in range(size[0]):
            self.cells[x][0] = 2
            self.cells[x][size[1]-1] = 2
        for y in range(2, size[1]-1):
            self.cells[0][y] = 2
            self.cells[size[0]-1][y] = 2
            
    def check_move(self, pos, chars):
        for x_offset in range(len(chars[0])):
            for y_offset in range(len(chars)):
                c = self.cells[pos[0]+x_offset][pos[1] + y_offset]
                if c > 0 and chars[y_offset][x_offset] != ' ':
                    return c
        return 0
    
    def __getitem__(self, item):
        return self.cells[item]
        
        
class FigureManager(Listener):
    def __init__(self, field, tetris, dispatcher, building):
        self.field = field
        self.tetris = tetris
        self.dispatcher = dispatcher
        self.building = building
    
    def on_event(self, event):
        if event.event_type == 'request_destruction':
            self.destroy_figure(event.event_value)
        elif event.event_type == 'request_installation':
            self.stop_figure(event.event_value)
    
    def create_figure(self):
        fig_widget = Attractee([['*', '*'], ['*', '*']],
                               [['red', 'red'], ['red', 'red']],
                                field=self.field, vx=0, vy=0,
                               tetris=self.tetris)
        self.terminal.add_widget(fig_widget, (30, 40), layer=2)
        self.dispatcher.register_listener(fig_widget, 'tick')
    
    def destroy_figure(self, widget):
        self.terminal.remove_widget(widget)
        self.dispatcher.unregister_listener(widget, 'all')
        self.create_figure()
        
    def stop_figure(self, widget):
        """
        Remove figure widget, give its cells to the building and set tetris'
        cells to 1 where there was a figure element
        :param widget:
        :return:
        """
        pos = self.terminal.widget_locations[widget].pos
        self.building.add_figure(widget, pos)
        for x_offset in range(widget.width):
            for y_offset in range(widget.height):
                if widget.chars[y_offset][x_offset] != ' ':
                    self.tetris[pos[0]+x_offset][pos[1]+y_offset] = 1
        self.destroy_figure(widget)


class BuildingWidget(Widget):
    """
    A widget that displays all the already installed blocks
    
    It only *displays* them, ie any logic is in TetrisSystem or widgets' code
    """
    def __init__(self, size):
        chars = [['.' for x in range(size[0])] for y in range(size[1])]
        colors = copy_shape(chars, 'dark gray')
        super().__init__(chars, colors)
    
    def add_figure(self, figure, pos):
        for y_offset in range(figure.height):
            for x_offset in range(figure.width):
                if figure.chars[y_offset][x_offset] != ' ':
                    self.chars[pos[1]+y_offset][pos[0]+x_offset] =\
                        figure.chars[y_offset][x_offset]
                    self.colors[pos[1]+y_offset][pos[0]+x_offset] = \
                        figure.colors[y_offset][x_offset]
        if self.terminal:
            self.terminal.update_widget(self)
    
    def remove_region(self, pos, shape):
        pass
    
    
class Attractor(Widget):
    def __init__(self, *args, mass=100, field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mass = mass
        self.field = field
        self.dragged = False
        # Position where the mouse was when it was grabbed
        # Easier than store a position of mouse relative to self.pos and recalc
        # every TK_MOUSE_MOVE
        self.grab_pos = (0, 0)
        
    def on_event(self, event):
        if event.event_type == 'key_down':
            if event.event_value == 'TK_MOUSE_LEFT':
                # Mouse left down, check if need to drag
                mouse_x = self.terminal.check_state('TK_MOUSE_X')
                mouse_y = self.terminal.check_state('TK_MOUSE_Y')
                pos = self.terminal.widget_locations[self].pos
                if pos[0] <= mouse_x <= pos[0] + self.width and \
                        pos[1] <= mouse_y <= pos[1] + self.height:
                    self.dragged = True
                    self.grab_pos = (mouse_x, mouse_y)
        elif event.event_type == 'key_up':
            if event.event_value == 'TK_MOUSE_LEFT':
                if self.dragged:
                    self.dragged = False
        elif event.event_type == 'misc_input':
            if event.event_value == 'TK_MOUSE_MOVE' and self.dragged:
                mouse_x = self.terminal.check_state('TK_MOUSE_X')
                mouse_y = self.terminal.check_state('TK_MOUSE_Y')
                if mouse_x != self.grab_pos[0] or \
                        mouse_y != self.grab_pos[1]:
                    pos = self.terminal.widget_locations[self].pos
                    shift = (mouse_x-self.grab_pos[0], mouse_y - self.grab_pos[1])
                    self.terminal.move_widget(self,
                                (pos[0]+shift[0], pos[1]+shift[1]))
                    self.grab_pos = (self.grab_pos[0]+shift[0],
                                     self.grab_pos[1]+shift[1])
                    self.terminal.refresh()
                    self.field.move_attractor(self,
                                          (pos[0]+shift[0], pos[1]+shift[1]))
                    
                    
class Attractee(Widget):
    def __init__(self, *args, field=None, vx=1, vy=1, tetris=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = field
        self.tetris = tetris
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
        
    def on_event(self, event):
        if event.event_type == 'tick':
            self.x_waited += event.event_value
            self.y_waited += event.event_value
            xpos, ypos = self.parent.widget_locations[self].pos
            self.vx += self.field[xpos][ypos].ax * event.event_value
            self.vy += self.field[xpos][ypos].ay * event.event_value
            if self.vx != 0:
                self.x_delay = abs(1 / self.vx)
            if self.vy != 0:
                self.y_delay = abs(1 / self.vy)
            if self.x_waited >= self.x_delay and self.vx != 0:
                new_x = xpos + round(self.vx/abs(self.vx))
                self.x_waited = 0
            else:
                new_x = xpos
            if self.y_waited >= self.y_delay and self.vy != 0:
                new_y = ypos + round(self.vy/abs(self.vy))
                self.y_waited = 0
            else:
                new_y = ypos
            if new_x != xpos or new_y != ypos:
                t = self.tetris.check_move((new_x, new_y), self.chars)
                print(t)
                if t == 0:
                    self.parent.move_widget(self, (new_x, new_y))
                elif t == 1:
                    return BearEvent(event_type='request_installation',
                                     event_value=self)
                elif t == 2:
                    return BearEvent(event_type='request_destruction',
                                     event_value=self)
