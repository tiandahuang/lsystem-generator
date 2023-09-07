import ctypes
import os
import time
import argparse
import math
import random
import subprocess
import logging

from lsys_types import *


class PaperPress():
    """
    generate and change wallpaper
    """

    INKSCAPE_PATH =         r'C:\Program Files\Inkscape\bin\inkscape'
    DEFAULT_SAVE_DIR =      r'images'
    WALLPAPER_STAGING_DIR = r'staging'
    DEMO_TYPES = {
            'sierpinski':       {'class':Sierpinski,        'default_name':'sierpinski.svg'},
            'dragon':           {'class':Dragon,            'default_name':'dragon.svg'},
            'plant':            {'class':Plant,             'default_name':'plant.svg'},
            'sierpinski_approx':{'class':SierpinskiApprox,  'default_name':'sierpinski_approx.svg'},
            'hilbert':          {'class':Hilbert,           'default_name':'hilbert.svg'},
            'levy':             {'class':Levy,              'default_name':'levy.svg'}}


    def __init__(self, type_select, fname=None, wallpaper=False) -> None:
        self.type_select = type_select
        if wallpaper:
            fname = os.path.join(self.WALLPAPER_STAGING_DIR, 'wallpaper.svg')
        self.fname = fname

    def generate(self, type_select=None, **kwargs):
        """
        kwargs: fname=None, file_prefix=None, save_dir=None, max_attempts=4
        """

        if type_select is None: type_select = self.type_select
        if type_select == 'rand':
            name, fname = self._generate_rand(**kwargs)
        else:
            name, fname = self._generate_demo(type_select, **kwargs)

        self.name = name
        if self.fname is None: self.fname = fname

        return self
    
    def set_wallpaper(self, fname=None):
        if fname is None: fname = self.fname

        root, ext = os.path.splitext(fname)

        if ext == '.svg':
            subprocess.run([self.INKSCAPE_PATH,
                            f'--export-filename={os.path.abspath(fname)}',
                            '--export-margin=10',
                            f'{os.path.abspath(fname)}'])
            
            subprocess.run([self.INKSCAPE_PATH,
                            f'--export-filename={os.path.abspath(root + ".png")}',
                            '--export-background=#181818',
                            '--export-height=1440',
                            f'{os.path.abspath(fname)}'])
    
        with open(os.path.join(self.WALLPAPER_STAGING_DIR, 'wallpaper.log', 'a')) as f:
            f.write(f'{self.name}\n')

        SPI_SETDESKWALLPAPER = 20
        return ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                f'{root + ".png"}',
                0)
    
    def _generate_demo(self, type_select, fname=None):
        if fname is None: fname = self.fname
        if fname is None: fname = os.path.join(self.DEFAULT_SAVE_DIR, 
                                               self.DEMO_TYPES[type_select]['default_name'])
        
        logging.info(f'Generating: {type_select}')

        self.DEMO_TYPES[type_select]['class']().run(fname)

        logging.info('Generating: Finished')

        return type_select, fname
    
    def _generate_rand(self, fname=None, file_prefix=None, save_dir=None, max_attempts=4):
        if save_dir is None: save_dir = self.DEFAULT_SAVE_DIR
        if file_prefix is None: file_prefix = str(int(time.time())) + '_'
        if fname is None: fname = self.fname

        for attempt in range(max_attempts):
            try:
                lsys = RandomLSystem()
                rules = f'start({lsys.start})_F({lsys.rules["F"]})_G({lsys.rules["G"]})_X({lsys.rules["X"]})_angle({lsys.angles[0]:.2f}_{lsys.angles[1]:.2f})'
                logging.info(f'Generating: {rules}')

                if fname is None: fname = os.path.join(save_dir, f'{file_prefix}{rules}.svg')
                lsys.run(fname)
                break
            except RuntimeError as e:
                logging.warning(e)
                logging.warning('Generation Failed: Retrying...')
            if attempt == max_attempts-1: raise RuntimeError('Too many generation failures')

        return rules, fname
    
if __name__ == '__main__':
    random.seed()
    epilog = '🟥🟧🟨🟩🟦🟪🟦🟩🟨🟧'
    epilog_tiled = ( epilog * (math.ceil(os.get_terminal_size()[0]/len(epilog))//2) )[:os.get_terminal_size()[0]//2]
    parser = argparse.ArgumentParser(
        prog='WallpaperGenerator',
        epilog=epilog_tiled,
    )

    parser.add_argument('-t', '--type',
                        default='rand',
                        choices=list(PaperPress.DEMO_TYPES.keys())+['rand', 'alldemo'])
    parser.add_argument('-f', '--filename')
    parser.add_argument('-r', '--rand_file_prefix', default='')
    parser.add_argument('-n', '--rand_generate_multi', default=1, type=int)
    parser.add_argument('-w', '--set_wallpaper', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    args = parser.parse_args()

    logging_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=logging_levels[min(args.verbose, len(logging_levels) - 1)])

    rand_save_dir = ''

    if args.set_wallpaper:
        if args.type == 'alldemo':  # set to random demo
            args.type = random.choice(list(PaperPress.DEMO_TYPES.keys()))
        args.rand_generate_multi = 1
        PaperPress(args.type, wallpaper=args.set_wallpaper).generate().set_wallpaper()
    else:
        if args.type == 'alldemo':
            for t in PaperPress.DEMO_TYPES.keys():
                PaperPress(t, args.filename).generate()
        elif args.type == 'rand':
            for i in range(args.rand_generate_multi):
                PaperPress('rand', args.filename).generate(file_prefix=args.rand_file_prefix)
        else:   # demo type
            PaperPress(args.type, args.filename).generate()

