#!/usr/bin/env python3
import sys
import time
import numpy.linalg
import numpy.random
import random


VK_SPREAD = [
    [-24, 58.0], [-23, 36.0], [-22, 20.0], [-21, 17.0],
    [-20, 16.0], [-19, 19.0], [-18, 24.0], [-17, 36.0],
    [-16, 45.0], [-15, 55.0], [-14, 60.0], [-13, 70.0],
    [-12, 75.0], [-11, 79.0], [-10, 83.0], [-9, 87.0],
    [-8, 92.0], [-7, 96.0], [-6, 100.0], [-5, 105.0],
    [-4, 108.0], [-3, 105.0], [-2, 96.0], [-1, 80.0],
    [0, 58.0], [1, 36.0], [2, 20.0], [3, 17.0],
    [4, 16.0], [5, 19.0], [6, 24.0], [7, 36.0],
    [8, 45.0], [9, 55.0], [10, 60.0], [11, 70.0],
    [12, 75.0], [13, 79.0], [14, 83.0], [15, 87.0],
    [16, 92.0], [17, 96.0], [18, 100.0], [19, 105.0],
    [20, 108.0], [21, 105.0], [22, 96.0], [23, 80.0],
    [24, 58.0], [25, 36.0], [26, 20.0], [27, 17.0],
    [28, 16.0], [29, 19.0], [30, 24.0], [31, 36.0],
    [32, 45.0], [33, 55.0], [34, 60.0], [35, 70.0],
    [36, 75.0], [37, 79.0], [38, 83.0], [39, 87.0],
    [40, 92.0], [41, 96.0], [42, 100.0], [43, 105.0],
    [44, 108.0], [45, 105.0], [46, 96.0], [47, 80.0],
    [48, 58.0],
]


def WR_params(date, f=1):
    """
        Generates params for WeightRandom class
    """
    tm = time.localtime(date)
    date = (tm.tm_hour * 60 + tm.tm_min) * 60 + tm.tm_sec
    return [
        [date, 0.0],
        [date + (3600 + 600) / f, 3200],
        [date + (2 * 3600) / f, 1850]
    ]


class PyWeightRandom:
    """
        use post date and time of publish
        to generate weight random method()
        it emulates when user creates reposts/likes
    """

    def __init__(self, data):
        """
            data = [
              [ x0 , y0 ] , - левая точка нуля пораболы
              [ x1 , y1 ] , - пик
              [ x2 , y2 ] - точка после точки пика через ( x1-x0 )
            ]
            endpoint = mun of second that:
             1. > x0
             2. <= x0 + 86000
        """
        # p = [ x0 , x1 , y1 , y2]
        self.p = [data[0][0], data[1][0], data[1][1], data[2][1]]
        mm = [
            [self.p[0]**2, self.p[0], 1],
            [self.p[1]**2, self.p[1], 1],
            [(2 * self.p[1] - self.p[0])**2, (2 * self.p[1] - self.p[0]), 1]
        ]
        abc = list(numpy.linalg.solve(mm, [0, self.p[2], 0]))
        self.a = abc[0]
        self.b = abc[1]
        self.c = abc[2]
        mm = [
            [1.0, -self.p[2]],
            [1.0, -self.p[3]]
        ]
        dk = numpy.linalg.solve(mm, [self.p[2] * self.p[1], self.p[3] * (2 * self.p[1] - self.p[0])])
        self.d = dk[0]
        self.k = dk[1]

        self.data = {}
        self._fill()

        self._weight = list(self.data.values())
        self._m = sum(self._weight)
        self.elem = list(self.data.keys())
        self.weight = list(map(lambda x: float(x) / float(self._m), self._weight))

    # ==========================================================================
    #                            INTERNAL METHODS
    # ==========================================================================

    def spread(self, x):
        """
            формула распределения случайно величиный
            p = [
             0 - start point (flaot)
             1 - X where max of Y (float)
             2 - max of Y (float)
             3 - Y when x = ( 2*p[1]-p[0] )
            ]
        """
        if self.p[0] + 1 <= x <= self.p[1] + 1:
            res = self.a * (x**2) + self.b * x + self.c
        elif self.p[1] <= x:
            res = (self.d / (x + self.k))
        else:
            res = self.spread(x + 3600 * 24)
        return res

    def _fill(self):
        """
            should fill self.data with values of spread function in interesing range
            return None
        """
        end = 86400 + (i := self.p[0])
        while i < end:
            self.data[i % 86400] = self.spread(i)
            i += 1

    def random(self, y=1):
        """
            return random number using spread function
        """
        if y <= 1:
            x = random.random()
            i = 0
            while x > 0.0:
                x -= self.weight[i]
                i += 1
            return [i - 1]
        else:
            k = float(self._m) / float(y)
            x = []
            y = k
            for i in range(len(ww := list(self._weight))):
                while ww[i] > 0.0:
                    y -= (z := min(y, ww[i]))
                    ww[i] -= z
                    if y <= 0.0:
                        y = k
                        x.append(ww[i])
            return x

    def destruct(self):
        """
            really do nothing (here)
        """
        pass

    def will_be(self, count_now, now):
        """
            predict now many obj will be in 24 hours
        """
        def en(_time):
            tm = time.localtime(_time)
            return (tm.tm_hour * 60 + tm.tm_min) * 60 + tm.tm_sec
        if (now := en(now)) < self.p[0]:
            now += 24 * 3600

        return (
            (count_now * sum(self.weight) / s)
            if (
                s := sum(
                    self.weight[i]
                    for i in range(len(self.weight))
                    if self.p[0] < i < now
                )
            ) > 0 else
            0
        )


def py__interpolice(ff, x):
    """
        real interpolice method
        USE ONLY BY INTERPOLICE
    """
    res = 0.0
    for i in ff:
        if not(-12 < (i[0] - x) < 12):
            continue
        li = 1.0
        for j in ff:
            if not(-12 < (j[0] - x) < 12):
                continue
            if i[0] != j[0]:
                z = (i[0] - j[0])
                li *= ((x - j[0]) / z)
        res += li * i[1]
    return res


boo = False
if sys.platform in {'linux', 'darwin'} and '--no-c' not in sys.argv[1:]:
    try:
        from .ext import interpolice as __interpolice
        from .ext import CWeightRandom as WeightRandom
        boo = True
    except Exception:
        pass

if not boo:
    WeightRandom = PyWeightRandom
    __interpolice = py__interpolice


def interpolice(x, ff=None):
    """
        takes as x float() - number of hours
          13:30 - 13.5
        return float from [0..1]
        ff = [
         [x0 , f(x0)],
         [x1 , f(x1)],
        ]
    """
    if ff is None:
        ff = VK_SPREAD
        _max = 108.0
    else:
        _max = float(max(i[1] for i in ff))
    return __interpolice(ff, x) / _max
