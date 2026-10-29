"""Collquan: сохранённые команды."""

from charmpkk.terminals import CollquanShell
import shlex as _shlex

@CollquanShell.register('setup', 'cmd block (4)')
def cmd_setup(args):
    from charmpkk.terminals import CollquanShell as _CS
    _sh = _CS()
    for _line in ['echo Starting', 'files mkdir ./build', 'files list .', 'echo Done']:
        _p = _shlex.split(_line)
        _sh.execute(_p[0] if _p else '', _p[1:] if _p else [], raw=_line)

