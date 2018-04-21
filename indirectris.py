#! /usr/bin/env python3.6

import sys

from bear_hug.bear_hug import BearTerminal, BearLoop
from bear_hug.event import BearEventDispatcher
from bear_hug.resources import XpLoader, Atlas
from bear_hug.widgets import Widget, ClosingListener, Label,Listener, \
    LoggingListener, FPSCounter

from gravity import GravityField, Attractor, Attractee, TetrisSystem, \
    FigureManager, BuildingWidget


class Refresher(Listener):
    """
    A simple listener that refreshes terminal every tick to prevent other
    widgets from doing so several times a tick
    """
    def __init__(self, t):
        self.terminal = t
        
    def on_event(self, event):
        if event.event_type == 'service' and event.event_value == 'tick_over':
            self.terminal.refresh()
            
# Standart BLT boilerplate
t = BearTerminal(font_path='cp437_12x12.png', size='60x45', title='Indirectris',
                 filter=['keyboard', 'mouse'])
dispatcher = BearEventDispatcher()
dispatcher.register_event_type('request_destruction')
dispatcher.register_event_type('request_installation')
loop = BearLoop(t, dispatcher)
dispatcher.register_listener(ClosingListener(), ['misc_input', 'tick'])

# Game objects
atlas = Atlas(XpLoader('indirectris.xp'), 'indirectris.json')
field = GravityField((60, 45))
building = BuildingWidget((60, 45))
tetris = TetrisSystem((60, 45))
figures = FigureManager(field=field,
                        tetris=tetris,
                        dispatcher=dispatcher,
                        building=building,
                        atlas=atlas)
figures.register_terminal(t)
dispatcher.register_listener(figures, ['request_destruction',
                                       'request_installation'])

building.add_figure(Widget([['*', '*'], ['*', '*']],
                     [['blue', 'blue'], ['blue', 'blue']]), pos=(25, 25))
tetris[25][25] = 1
tetris[25][26] = 1
tetris[26][25] = 1
tetris[26][26] = 1
attractor = Attractor(*atlas.get_element('attractor'),
                      field=field, mass=150)
field.add_attractor(attractor, (10, 25))
attractor2 = Attractor(*atlas.get_element('attractor'),
                      field=field, mass=150)
field.add_attractor(attractor2, (50, 25))
dispatcher.register_listener(attractor, ['misc_input', 'key_up', 'key_down'])
dispatcher.register_listener(attractor2, ['misc_input', 'key_up', 'key_down'])

# Debug stuff
logger = LoggingListener(sys.stdout)
fps = FPSCounter()
dispatcher.register_listener(fps, 'tick')
dispatcher.register_listener(logger, 'key_up')
r = Refresher(t)
dispatcher.register_listener(r, 'service')

t.start()
figures.create_figure()
t.add_widget(building, pos=(0, 0), layer=0)
t.add_widget(attractor, pos=(10, 25), layer=1)
t.add_widget(attractor2, pos=(50, 25), layer=3)
t.add_widget(fps, pos=(0, 44), layer=1)
loop.run()
