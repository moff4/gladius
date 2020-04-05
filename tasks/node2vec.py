
from typing import Any

from node2vec.edges import HadamardEmbedder
from node2vec import Node2Vec

from conf import conf
from logic.graph import GRAPH


ARGS = {}

task_description = 'train Node2Vec; args: %s' % ', '.join(list(ARGS))


def train(model_filename: str, embeding_filename: str, edges_filename: str, **params: Any):
    graph = GRAPH.graph
    node2vec = Node2Vec(graph, dimensions=64, walk_length=30, num_walks=200, workers=8)
    model = node2vec.fit(window=10, min_count=1, batch_words=4)
    model.wv.save_word2vec_format(embeding_filename)
    model.save(model_filename)
    edges_embs = HadamardEmbedder(keyed_vectors=model.wv)
    edges_kv = edges_embs.as_keyed_vectors()
    edges_kv.save_word2vec_format(edges_filename)


def start():
    try:
        train(**conf.node2vec)
    except KeyboardInterrupt:
        ...
