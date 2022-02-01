import pytest

from src.pycpre.lazy_sequence import LazySequence
import gc


def test_simple_generator():
    def squares(n: int):
        for i in range(1, n + 1):
            yield i * i

    ls = LazySequence(squares(5))
    assert ls.index == 0
    assert len(ls.state.buffer) == 0
    assert len(ls.state.heads) == 1
    assert ls.state.index_of_0 == 0

    assert ls[1] == 4

    assert ls.index == 0
    assert len(ls.state.buffer) == 2
    assert len(ls.state.heads) == 1
    assert ls.state.index_of_0 == 0

    tmp = ls[2:]

    assert ls.index == 0
    assert tmp.index == 2
    assert len(ls.state.heads) == 2
    assert len(ls.state.buffer) == 2
    assert ls.state.index_of_0 == 0

    ls = tmp
    del tmp
    gc.collect()

    assert ls.index == 2
    assert len(ls.state.heads) == 1
    assert len(ls.state.buffer) == 0
    assert ls.state.index_of_0 == 2

    assert ls[0] == 9
    assert ls[1] == 16
    assert ls[2] == 25
    with pytest.raises(IndexError):
        assert ls[3] == 36

    assert ls[:10] == [9, 16, 25]
    assert ls[1:2] == [16]
