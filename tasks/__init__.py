from tasks import shell
from tasks import server
from tasks import ranks
from tasks import clustering
from tasks import pather
from tasks import graph
from tasks import node2vec

TASKS = {
    'shell': shell,
    'server': server,
    'ranks': ranks,
    'clustering': clustering,
    'pather': pather,
    'graph': graph,
    'node2vec': node2vec,
}
