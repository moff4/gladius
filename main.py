#!/usr/bin/env python3.8

import sys
import asyncio

from k2.logger import BaseLogger as logger

from conf import conf
from tasks import TASKS

HELP_MSG = '''
Gladius - recomendation system

$ ./main.py [commands] [flags]

Flags:
-h, --help, -?  - see this msg again
-s, --server    - start web-server
--create-tables - create sql tables
--no-c          - do not use C extension

Commands:
''' + '\n'.join(
    [
        '%s   \t- %s' % (
            key,
            (
                handler.task_description
                if hasattr(handler, 'task_description') else
                'no task description'
            ),
        )
        for key, handler in TASKS.items()
    ]
) + '\n'


def setup():
    conf.sql.generate_mapping(create_tables='--create-tables' in sys.argv)


def run_task(task_name, f):
    try:
        f()
    except Exception as e:
        asyncio.run(logger.exception('"{}" exception: {}', task_name, e))


def main():
    fs = [(i, TASKS[i].start) for i in sys.argv if i in TASKS]
    if not fs:
        print('no tasks to run')
        return
    setup()

    for i, f in fs:
        run_task(i, f)


if __name__ == '__main__':
    print(HELP_MSG) if set(sys.argv) & {'-h', '--help', '-?'} else main()
