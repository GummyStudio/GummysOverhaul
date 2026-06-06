""" mmm.. some good ol dialogue text. """

import bascenev1 as bs
import bauiv1 as bui

class DialogText:
    def __init__(self, 
                text: str, 
                position=(0, 0), 
                delay: float = 0.05, 
                color=(1, 1, 1),
                h_align: str = 'left',
                scale: float = 1.1,
                sound: str = 'basictxt',
                ):
        """
        Display text letter by letter, like an RPG dialogue box.
        :param text: The full text to display
        :param position: (x, y) position
        :param delay: Time between letters
        :param color: RGB color tuple
        :param h_align: Horizontal alignment
        :param sound: Sound to play on every letter
        """
        self.full_text = text
        self.displayed = ""
        self.index = 0
        self.delay = delay
        self.finished = False
        self.sound = sound
        

        self.node = bs.newnode(
            'text',
            attrs={
                'text': '',
                'position': position,
                'scale': scale,
                'h_align': h_align,
                'v_align': 'center',
                'color': color,
                'shadow': 0.6,
                'flatness': 0.5,
            },
        )

        # Begin typing effect
        self._tick()

    def _tick(self):
        if self.index < len(self.full_text):
            try:
                self.displayed += self.full_text[self.index]
                self.node.text = self.displayed
                self.index += 1
                bs.timer(self.delay, self._tick)
                # If the sound is already a sound dont get sound lmfao
                if isinstance(self.sound, bs.Sound):
                    self.sound.play(1.5)
                else:
                    bs.getsound(self.sound).play()
            except:
                pass
        else:
            self.finished = True