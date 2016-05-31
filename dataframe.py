"""Data frame for convinient work and renderings multipage data."""

import math


class DataFrame(list):
    """Data represents as granulated list of lists.
    DataFrame is a list, thus you can access elements directly like
    with original list structure: dataframe[index] -> element
    Also you can granulate (more than once) list of frames by frame length
    Default representation: DataFrame([1, 2, 3]) -> [[1], [2], [3]]
    Granulate by 2: DataFrame([1, 2, 3]).granulate(2) -> [[1, 2], [3]]
    Internals:
        _frames: a list of lists, each frame is slice of data with
            frame length
        _findex: index of current frame (_frames[_findex])
        _index: index of current element (self[_index])
        _flen: length of frame
    """
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._frames = [[frame] for frame in self]
        self._findex = 0 if self._frames else None
        self._index = 0 if self._frames else None
        self._flen = 1

    def granulate(self, length):
        """Granulate list by frames (lists) of a given length.
        :param length: length for granulating
        :type length: int
        """
        if length == self._flen:
            return

        self._flen = length
        frame_count = int(math.ceil(len(self) / float(length)))
        #TODO: Recalculate findex (index will be the same)
        new_findex = 0
        frames = []
        for frame in xrange(frame_count):
            frames.append(self[frame * length:frame * length + length])
        self._frames = frames
        self._findex = new_findex
        self._index = 0  # temporary

    def move_next(self, step=1):
        """Move global index first, then move frame index.
        :param step: step to move at
        :type step: int
        :return: next element if that element exists, None otherwise
        :rtype: object or None
        """
        if self._index is not None and len(self) > self._index + step:
            self._index += step
            # if index >= end index of current frame --> recalculate findex
            if self._index >= self._findex * self._flen + self._flen:
                self._findex += int(math.ceil(step / float(self._flen)))
            return self[self._index]
        return None

    def move_prev(self, step=1):
        """Move global index first, then move frame index.
        :param step: step to move at
        :type step: int
        :return: previous element if that element exists, None otherwise
        :rtype: object or None
        """
        if self._index is not None and self._index - step >= 0:
            self._index -= step
            # if index <= start index of current frame --> recalculate findex
            if self._index < self._findex * self._flen:
                self._findex -= int(math.ceil(step / float(self._flen)))
            return self[self._index]
        return None

    def next_frame(self, save_index=True):
        """Move frame first, then move global index to corresponding place.
        :return: next frame if that frame exists, None otherwise
        :rtype: list or None
        """
        if len(self._frames) > self._findex + 1:
            self._findex += 1
            frame_start = self._findex * self._flen
            if not save_index:
                self._index = frame_start
            else:
                if self._index + self._flen <= len(self) - 1 and save_index:
                    self._index += self._flen
                else:
                    self._index = frame_start + len(self.frame) - 1
            return self._frames[self._findex]
        return None

    def prev_frame(self, save_index=True):
        """Move frame first, then move global index to corresponding place.
        :return: previous frame if that frame exists, None otherwise
        :rtype: list or None
        """
        if self._findex > 0:
            self._findex -= 1
            frame_end = self._findex * self._flen + self._flen -1
            if not save_index:
                self._index = frame_end
            else:
                self._index -= self._flen
            return self._frames[self._findex]
        return None

    def frames_count(self):
        """Number of frames.
        :return: number of frames
        :rtype: int
        """
        return len(self._frames)

    @property
    def frame(self):
        """Return current frame.
        :return: current frame if len(self) > 0, empty list otherwise
        :rtype: list
        """
        return self._frames[self._findex] if self._frames else []

    @property
    def frame_index(self):
        """Return current frame index.
        :return: current frame index
        :rtype: integer or None
        """
        return self._findex

    @property
    def element(self):
        """Return current element.
        :return: current element if exists, None otherwise
        :rtype: object or None
        """
        return self[self._index] if self._index is not None else None

    @property
    def element_index(self):
        """Return current element index.
        :return: current element index
        :rtype: integer or None
        """
        return self._index


if __name__ == "__main__":
    import unittest

    class TestDataFrame(unittest.TestCase):
        """Basic test."""
        def test_empty(self):
            """Empty dataframe."""
            dframe = DataFrame()
            self.assertEqual(dframe, [])
            self.assertEqual(dframe.frame, [])
            self.assertEqual(dframe.element_index, None)
            self.assertEqual(dframe.frame_index, None)

        def test_operations(self):
            """Basic operations."""
            data = list(range(21))
            dframe = DataFrame(data)
            self.assertEqual(len(dframe), 21)
            dframe.granulate(5)
            self.assertEqual(dframe.frames_count(), 5)
            self.assertEqual(len(dframe.frame), 5)
            self.assertEqual(dframe.element_index, 0)
            self.assertEqual(dframe.frame_index, 0)

            self.assertEqual(dframe.next_frame(), list(range(5, 10)))

    unittest.main()
    sys.exit(0)
