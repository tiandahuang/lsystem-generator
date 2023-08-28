from typing import Callable
from svg_turtle import SvgTurtle
import subprocess
import numpy as np
import functools as ft

class LSystem():
    """
    https://en.wikipedia.org/wiki/L-system
    """

    INKSCAPE_PATH = r'C:\Program Files\Inkscape\bin\inkscape'

    def __init__(self,
                 variables : str,
                 constants : str,
                 start : str,
                 rules : dict[str, str]) -> None:
        
        self.variables = variables
        self.constants = constants
        self.start = start
        self.rules = rules

        for c in constants:
            self.rules[c] = c

    def generate(self, iters : int, cont : bool = False) -> str:
        curr_iter = self.saved_state if cont else self.start
        for i in range(iters):
            next_iter = ''
            for c in curr_iter:
                if c in self.rules:
                    next_iter += self.rules[c]
            curr_iter = next_iter
        self.saved_state = curr_iter
        return curr_iter
    
    def graph(self,
              t : SvgTurtle,
              turtle_cmd : str,
              turtle_cmd_lut : dict[str, Callable],
              fname : str) -> None:
        
        for idx, c in enumerate(turtle_cmd):
            turtle_cmd_lut[c](idx)
        
        t.save_as(fname)
        self._crop_to_boundary(fname)

    @staticmethod
    def _crop_to_boundary(fname, new_fname=None):
        if new_fname is None: new_fname = fname
        subprocess.run([LSystem.INKSCAPE_PATH,
                        '--export-area-drawing',
                        f'--export-plain-svg={new_fname}',
                        f'{fname}'])
        
class GraphingTools():

    PENCOLOR_STEPS = 3000

    def __init__(self, color_table : str) -> None:
        # color_table : rgb, rgbw

        self.steps = GraphingTools.PENCOLOR_STEPS

        if color_table == 'rgb':
            self.pencolor_lookup_table = self._pencolor_init('circle')
        elif color_table == 'rgbw':
            self.steps = 6000
            self.pencolor_lookup_table = self._pencolor_init('orbital')
        elif color_table == 'rg_blind':
            self.steps = 6000
            self.pencolor_lookup_table = self._pencolor_init('ellipse', squeeze=0.01, phase=-np.pi/3)
        
    def pencolor(self, x : int):
        return tuple(self.pencolor_lookup_table[x % self.steps])
    
    def _pencolor_init(self, functype : str, **kwargs):
        # functype : circle, ellipse, orbital
        # kwargs : squeeze, phase, coef (orbital)
        # TODO: fix ellipse velocity
        h = np.linspace(0, 2*np.pi, num=self.steps, endpoint=False)

        def ellipse(x, major=1.0, minor=1.0, rotate=0.0):
            a = np.ones(len(x)) * major
            b = np.ones(len(x)) * minor
            return ( (a**2 * b**2) / (b**2 * (np.cos(x + rotate))**2 + a**2 * (np.sin(x + rotate))**2) )**0.5
        
        def orbital(x, coef=2, rotate=0.0):
            return np.abs(np.cos(coef*x + rotate))
        
        types = {'circle':ft.partial(ellipse),
                 'ellipse':ft.partial(ellipse, minor=kwargs.get('squeeze', 1.0), rotate=kwargs.get('phase', 0.0)),
                 'orbital':ft.partial(orbital, coef=kwargs.get('coef', 6), rotate=kwargs.get('phase', 0.0))}
        f = types[functype]

        return self.hsv_polar_to_rgb(h, f(h), np.ones(len(h)))
    
    @staticmethod
    def hsv_polar_to_rgb(h : np.ndarray, s : np.ndarray, v : np.ndarray):
        def f(n : int):
            k = np.fmod((3 * h / np.pi) + n, 6)
            return v - v * s * np.clip(np.minimum(k, 4 - k), 0, 1)
        return np.vstack((f(5), f(3), f(1))).T

    @staticmethod
    def get_standard_turtle_commands(t : SvgTurtle, turn : tuple[float, float], color_table : str = 'rgb'):
        # color_table : rgb, rgbw

        # new turtle data structures
        t._save_state = []
        def save_state(self):
            state = (self.position(), self.heading())
            self._save_state.append(state)
        SvgTurtle.save_state = save_state

        def load_state(self):
            pos, head = self._save_state.pop()
            self.setposition(pos)
            self.setheading(head)
        SvgTurtle.load_state = load_state

        pen = GraphingTools('rgb')

        return {'F':lambda x: [t.pen(pencolor=pen.pencolor(x)), t.forward(1)],
                'G':lambda x: [t.pen(pencolor=pen.pencolor(x)), t.forward(1)],
                'A':lambda x: [t.pen(pencolor=pen.pencolor(x)), t.forward(1)],
                'B':lambda x: [t.pen(pencolor=pen.pencolor(x)), t.forward(1)],
                
                '+':lambda x: t.left(turn[0]),
                '-':lambda x: t.right(turn[1]),
                
                '[':lambda x: t.save_state(),
                ']':lambda x: [t.up(), t.load_state(), t.down()],
                
                'X':lambda x: None,
                'Y':lambda x: None,}
