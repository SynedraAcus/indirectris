"""
Various stuff not related to the basic gameplay cycle
"""

from bear_hug.widgets import Label


class ScoreCounter(Label):
    """
    Counts the score
    """
    def __init__(self, **kwargs):
        super().__init__('00000', color='#ff0000ff', *kwargs)
        self.score = 0
    
    def on_event(self, event):
        if event.event_type in ('h7', 'v7'):
            self.score += 10
            self.text = str(self.score).rjust(5, '0')
            if self.parent is self.terminal:
                self.terminal.update_widget(self, refresh=False)
        elif event.event_type == 'square':
            self.score += 15
            self.text = str(self.score).rjust(5, '0')
            if self.parent is self.terminal:
                self.terminal.update_widget(self, refresh=False)
