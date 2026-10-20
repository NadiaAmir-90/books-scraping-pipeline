import random
from typing import List, Sequence, TypeVar

T = TypeVar("T")

"""Selects random subsets of items."""
class RandomSelector:

    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    """Pick a random number of categories."""
    def choose_categories(self, items: Sequence[T], low: int = 5, high: int = 10) -> List[T]:
        count = min(self._rng.randint(low, high), len(items))
        return self._rng.sample(list(items), count)

    """Pick exactly `count` books """
    def choose_books(self, items: Sequence[T], count: int = 5) -> List[T]:
        return self._rng.sample(list(items), min(count, len(items)))