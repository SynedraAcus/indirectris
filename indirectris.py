#! /usr/bin/env python3.6

import sys

from bear_hug.bear_hug import BearTerminal, BearLoop
from bear_hug.event import BearEventDispatcher
from bear_hug.widgets import Widget, ClosingListener, Label,\
    LoggingListener, FPSCounter

from gravity import GravityField, Attractor, Attractee

t = BearTerminal(font_path='cp437_12x12.png', size='60x45', title='Indirectris',
                 filter=['keyboard', 'mouse'])
dispatcher = BearEventDispatcher()
loop = BearLoop(t, dispatcher)
dispatcher.register_listener(ClosingListener(), ['misc_input', 'tick'])

field = GravityField((60, 45))
attractor = Attractor([['#', '#'], ['#', '#']], [['red', 'red'], ['red', 'red']],
                      field=field, mass=150)
field.add_attractor(attractor, (10, 25))

attractor2 = Attractor([['#', '#'], ['#', '#']], [['red', 'red'], ['red', 'red']],
                      field=field, mass=150)
field.add_attractor(attractor2, (50, 25))
attractee = Attractee([['*', '*'], ['*', '*']], [['red', 'red'], ['red', 'red']],
                      field=field, vx=0, vy=0, attr=attractor)
dispatcher.register_listener(attractor, ['misc_input', 'key_up', 'key_down'])
dispatcher.register_listener(attractor2, ['misc_input', 'key_up', 'key_down'])
dispatcher.register_listener(attractee, 'tick')
logger = LoggingListener(sys.stdout)
fps = FPSCounter()
dispatcher.register_listener(fps, 'tick')
dispatcher.register_listener(logger, 'key_up')
t.start()
t.add_widget(attractor, pos=(10, 25), layer=1)
t.add_widget(attractor2, pos=(50, 25), layer=3)
t.add_widget(attractee, pos=(30, 40), layer=2)
t.add_widget(fps, pos=(0, 44), layer=1)
loop.run()
