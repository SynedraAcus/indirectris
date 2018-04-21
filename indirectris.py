#! /usr/bin/env python3.6

from bear_hug.bear_hug import BearTerminal, BearLoop
from bear_hug.event import BearEventDispatcher
from bear_hug.widgets import Widget, ClosingListener, Label

t = BearTerminal(font_path='cp437_12x12.png', size='60x45', title='Indirectris',
                 filter=['keyboard', 'mouse'])
dispatcher = BearEventDispatcher()
loop = BearLoop(t, dispatcher)
dispatcher.register_listener(ClosingListener(), ['misc_input', 'tick'])

t.start()
t.add_widget(Label('Test\nTest'), pos=(10, 10), layer=0)

loop.run()
