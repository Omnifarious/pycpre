#  This file is part of the pycpre distribution.
#  Copyright 2022 Eric Hopper
#
#  You may modify and/or redistribute this software under the terms of the GNU
#  General Public License version as published by the Free Software Foundation,
#  version 3 or greater.
#
#  You should have received a copy of the GNU General Public License along with
#  this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>

from collections.abc import Sequence
from typing import Generic, Iterable, Iterator, List, Optional, TypeVar, Union
from weakref import ref, ReferenceType

__all__ = ["LazySequence"]


T = TypeVar("T")


class _LazySequenceState(Generic[T]):
    def __init__(self, item_iterator: Iterator[T], **kwargs):
        super().__init__(**kwargs)
        self.buffer: List[T] = []
        self.iterator: Iterator[T] = item_iterator
        self.heads: List[ReferenceType[T]] = []
        self.index_of_0: int = 0

    def new_sequence(self, sequence: "LazySequence[T]") -> None:
        assert sequence.state is self
        if sequence.index < self.index_of_0:
            raise RuntimeError("LazySequence created that's attempting to time "
                               "travel to the past.")
        self.heads.append(ref(sequence, self._refdestroyed))

    def _refdestroyed(self, ref: ReferenceType[T]):
        try:
            refidx = self.heads.index(ref)
        except ValueError:
            return
        del self.heads[refidx]
        self.update_min()

    def update_min(self):
        newheads: List[ReferenceType[T]] = []
        min_idx: Optional[int] = None
        for seqref in self.heads:
            seq = seqref()
            if seq is not None:
                newheads.append(seqref)
            if min_idx is None or seq.index < min_idx:
                min_idx = seq.index
        assert min_idx >= self.index_of_0
        if min_idx > self.index_of_0:
            del self.buffer[0:min_idx]
            self.index_of_0 = min_idx

    def ensure_index(self, buffer_idx: int) -> T:
        if buffer_idx < self.index_of_0:
            return
        if (buffer_idx - self.index_of_0) >= len(self.buffer):
            for _ in range(len(self.buffer), buffer_idx + 1):
                self.buffer.append(next(self.iterator))
        assert (buffer_idx - self.index_of_0) < len(self.buffer)
        return self.buffer[buffer_idx - self.index_of_0]


class LazySequence(Sequence[T]):
    def __init__(self, item_iterator: Union["LazySequence[T]", Iterable[T]], **kwargs):
        if isinstance(item_iterator, LazySequence):
            self.state = item_iterator.state
            self.index = item_iterator.index
        else:
            self.state = _LazySequenceState(iter(item_iterator))
            self.index = 0
        self.state.new_sequence(self)

    def __reversed__(self):
        raise NotImplemented("Lazy sequences can't be reversed.")

    def __len__(self) -> int:
        raise NotImplemented("Lazy sequences may be infinitely long.")

    def __getitem__(self, index: Union[int, slice]) \
            -> Union[T, "LazySequence[T]", List[T]]:
        if isinstance(index, int):
            if index < 0:
                raise ValueError("Lazy sequences may not have an end and don't "
                                 "support indexing from the end.")
            try:
                return self.state.ensure_index(self.index + index)
            except StopIteration:
                raise IndexError(f"LazySequence index {index} out of range")
        else:
            if (index.start is not None and index.start < 0) or \
                    (index.stop is not None and index.stop < 0):
                raise ValueError("Lazy sequences may not have an end and don't "
                                 "support indexing from the end.")
            if index.step is not None and index.stop is None:
                raise ValueError("Lazy sequences do not support step slicing "
                                 "without an end.")
            start = index.start if index.start is not None else 0
            if index.stop is None:
                newseq = LazySequence(self)
                newseq.index += start
                return newseq
            else:
                stop = max(index.stop, start)
                start += self.index
                stop += self.index
                assert self.state.index_of_0 <= start
                try:
                    self.state.ensure_index(self.index + stop)
                except StopIteration:
                    pass
                start -= self.state.index_of_0
                stop -= self.state.index_of_0
                if index.step is None:
                    return self.state.buffer[start:stop]
                else:
                    return self.state.buffer[start:stop:index.step]
