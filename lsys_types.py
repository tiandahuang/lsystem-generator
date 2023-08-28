from svg_turtle import SvgTurtle
from lsystem import LSystem, GraphingTools
import random

class Dragon():
    def __init__(self, levels=10) -> None:
        variables = 'FG'
        constants = '+-'
        start = 'F'
        rules = {'F':'F+G', 'G':'F-G'}
        self.t = SvgTurtle(1e4, 1e4)
        self.turtle_cmd_lut = GraphingTools.get_standard_turtle_commands(self.t, (90, 90))

        self.ls = LSystem(variables, constants, start, rules)
        self.ls_str = self.ls.generate(levels)

    def run(self, fname):
        self.ls.graph(self.t, self.ls_str, self.turtle_cmd_lut, fname)

class Plant():
    def __init__(self, levels=10) -> None:
        variables = 'XF'
        constants = '+-[]'
        start = 'X'
        rules = {'X':'F_[[X]-X]-F[-FX]+X', 'F':'FF'}
        self.t = SvgTurtle(1e4, 1e4)
        self.turtle_cmd_lut = GraphingTools.get_standard_turtle_commands(self.t, (25, 25))

        self.ls = LSystem(variables, constants, start, rules)
        self.ls_str = self.ls.generate(levels)

    def run(self, fname):
        self.ls.graph(self.t, self.ls_str, self.turtle_cmd_lut, fname)

class Sierpinski():
    def __init__(self, levels=6) -> None:
        variables = 'FG'
        constants = '+-'
        start = 'F-G-G'
        rules = {'F':'F-G+F+G-F', 'G':'GG'}
        self.t = SvgTurtle(1e4, 1e4)
        self.turtle_cmd_lut = GraphingTools.get_standard_turtle_commands(self.t, (120, 120))

        self.ls = LSystem(variables, constants, start, rules)
        self.ls_str = self.ls.generate(levels)

    def run(self, fname):
        self.ls.graph(self.t, self.ls_str, self.turtle_cmd_lut, fname)

class SierpinskiApprox():
    def __init__(self, levels=8) -> None:
        variables = 'AB'
        constants = '+-'
        start = 'A'
        rules = {'A':'B-A-B', 'B':'A+B+A'}
        self.t = SvgTurtle(1e4, 1e4)
        self.turtle_cmd_lut = GraphingTools.get_standard_turtle_commands(self.t, (60, 60))

        self.ls = LSystem(variables, constants, start, rules)
        self.ls_str = self.ls.generate(levels)

    def run(self, fname):
        self.ls.graph(self.t, self.ls_str, self.turtle_cmd_lut, fname)

class Hilbert():
    def __init__(self, levels=6) -> None:
        variables = 'XY'
        constants = 'F+-'
        start = 'X'
        rules = {'X':'+YF-XFX-FY+', 'Y':'-XF+YFY+FX-'}
        self.t = SvgTurtle(1e4, 1e4)
        self.turtle_cmd_lut = GraphingTools.get_standard_turtle_commands(self.t, (90, 90))

        self.ls = LSystem(variables, constants, start, rules)
        self.ls_str = self.ls.generate(levels)

    def run(self, fname):
        self.ls.graph(self.t, self.ls_str, self.turtle_cmd_lut, fname)

class Levy():
    def __init__(self, levels=12) -> None:
        variables = 'F'
        constants = '+-'
        start = 'F'
        rules = {'F':'+F--F+'}
        self.t = SvgTurtle(1e4, 1e4)
        self.turtle_cmd_lut = GraphingTools.get_standard_turtle_commands(self.t, (45, 45))

        self.ls = LSystem(variables, constants, start, rules)
        self.ls_str = self.ls.generate(levels)

    def run(self, fname):
        self.ls.graph(self.t, self.ls_str, self.turtle_cmd_lut, fname)

class RandomLSystem():
    def __init__(self, levels=8, seed=None, symmetric=False) -> None:
        if seed is not None: random.seed(seed)

        variables = 'FGX'
        constants = '+-'
        self.start = RandomLSystem.rstring(2, 'FG')
        self.rules = {'F':RandomLSystem.rrule('FGX+-', 'G+-'),
                      'G':RandomLSystem.rrule('FGX+-', 'F'),
                      'X':RandomLSystem.rrule('FGX+-')}
        self.angles = RandomLSystem.rangle_pair(90, nice=False, mirror=True)
        self.t = SvgTurtle(1e4, 1e4)
        self.turtle_cmd_lut = GraphingTools.get_standard_turtle_commands(self.t, self.angles)

        self.ls = LSystem(variables, constants, self.start, self.rules)

        for i in range(5):
            if i == 4: raise RuntimeError(f'NonConverging LSystem Rules: {self.rules}')

            gen_out = self.ls.generate(levels)
            if len(gen_out) > 1e5: levels -= 1
            elif len(gen_out) < 1e4: levels += 1
            else: break
        
        self.ls_str = gen_out
    
    @staticmethod
    def rstring(len, elems):
        return ''.join(random.choice(elems) for _ in range(len))
    
    @staticmethod
    def rangle_pair(center, nice=False, mirror=False):
        def rand(): return random.gauss(mu=center, sigma=20)
        out = (round(rand()/15)*15, round(rand()/15)*15) if nice else (rand(), rand())
        return out if not mirror else (out[0], out[0])

    @staticmethod
    def rrule(elems, required=''):
        combined = required + RandomLSystem.rstring(random.randrange(1, 6), elems)
        return ''.join(random.sample(combined, k=len(combined)))
    
    def run(self, fname):
        self.ls.graph(self.t, self.ls_str, self.turtle_cmd_lut, fname)