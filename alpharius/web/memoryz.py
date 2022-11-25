import tracemalloc
from concurrent import futures

import flask

bp = flask.Blueprint('memoryz', __name__)
tracemalloc.start(5)


def _get_memory_stats():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')
    total = sum(stat.size for stat in top_stats)
    stats = {'total': total // (1024 * 1024), 'stats': []}
    limit = 9
    for index, stat in enumerate(top_stats[:limit], 1):
        mem_size = stat.size // (1024 * 1204)
        if mem_size == 0:
            limit = index
            break
        frame = stat.traceback[-1]
        s = {'index': index,
             'filename': frame.filename,
             'lineno': frame.lineno,
             'mem_size': mem_size}
        tracebacks = ['Traceback (most recent call first):']
        for line in stat.traceback.format(most_recent_first=True):
            tracebacks.append(line)
        s['traceback'] = '\n'.join(tracebacks)
        stats['stats'].append(s)
    other = top_stats[limit:]
    if other:
        stats['other'] = sum(stat.size for stat in other) // (1024 * 1024)


@bp.route('/memoryz')
def memoryz():
    with futures.ProcessPoolExecutor(max_workers=1) as pool:
        stats = pool.submit(_get_memory_stats).result()
    return flask.render_template('memoryz.html', stats=stats)
