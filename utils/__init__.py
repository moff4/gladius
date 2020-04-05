
import sys


def parse_args(default_args):
    args = dict(default_args)
    for arg in sys.argv[1:]:
        for key in args:
            if arg.startswith('--{}'.format(key)):
                arg = arg[len(key) + 2:]
                args[key] = arg[1:] if arg.startswith('=') else True
    return args
