import sys
from src.automator import Automator

if __name__ == '__main__':
    if sys.argv[1] == 'tg':
        automator = Automator(is_visible=False)
        automator.main_tg()
    elif sys.argv[1] == 're':
        automator = Automator(is_visible=True)
        automator.main_re()
