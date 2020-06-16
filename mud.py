#!/usr/bin/env python3

from os import chdir, listdir
from subprocess import check_output, run
from sys import argv


def c(*args):
    return check_output(args, universal_newlines=True).strip()


def get_tracking(gb_local, gb_remote):
    gt_base = c('git', 'merge-base', gb_local, gb_remote)
    gt_lref = c('git', 'rev-parse', gb_local)
    gt_rref = c('git', 'rev-parse', gb_remote)

    if gt_lref == gt_rref:
        return 0
    elif gt_lref == gt_base:
        return -1
    elif gt_rref == gt_base:
        return 1
    else:
        return 127

show_clean = len(argv) > 1 and argv[1] == '--include-clean'

for dir in listdir('.'):
    chdir(dir)

    gs_msg = ''
    gs = run(['git', 'status', '--porcelain', '2'],
             universal_newlines=True, capture_output=True)

    if gs.returncode != 0:
        gs_msg = '\x1B[1m\x1B[31mERROR'
    else:
        gb_local = c('git', 'symbolic-ref', 'HEAD').split('/')[-1]
        gb_remote = c('git', 'for-each-ref', '--format=%(upstream:short)',
                      c('git', 'symbolic-ref', '-q', 'HEAD'))

        if gb_remote:
            gt_pos = get_tracking(gb_local, gb_remote)
        else:
            gt_pos = -128

        if gs.stdout:
            gs_msg = '\x1B[33mDIRTY'
        elif gt_pos == -1:
            gs_msg = 'BEHIND'
        elif gt_pos == 1:
            gs_msg = 'AHEAD'
        elif gt_pos == 127:
            gs_msg = 'DIVERGED'
        elif gt_pos == -128:
            gs_msg = 'NO UPSTREAM'
        elif show_clean:
            gs_msg = '\x1B[32mCLEAN'

    if gs_msg:
        print("%-40s%s\x1B[0m" % (dir, gs_msg))

    chdir('..')
