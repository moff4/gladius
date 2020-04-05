
from typing import List

from logic.graph import GRAPH


def narrowness(tags: List[str]) -> float:
    if not tags:
        return 1.0
    GRAPH.multi_weight(
        (src, dst)
        for src in tags
        for dst in tags
    )
    res =  (
        sum(
            weights := [
                GRAPH.weight(src, dst)
                for src in tags
                for dst in tags
                if src != dst
            ]
        ) / len(weights)
    )
    GRAPH.save()
    return res
