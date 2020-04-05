#!/usr/bin/env python3
import ctypes
import numpy.linalg
import random

mod = ctypes.CDLL(r'ext/utils.so')

"""
    double interpolice(double, double* , double*,int);
"""
__interpolice = ctypes.CFUNCTYPE(
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_int,
)(('interpolice', mod))

"""
    weight_random_t* weight_random_create(long double*,long double*,long double*);
"""
_weight_random_create = ctypes.CFUNCTYPE(
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_longdouble),
    ctypes.POINTER(ctypes.c_longdouble),
    ctypes.POINTER(ctypes.c_longdouble),
)(('weight_random_create', mod))

"""
    int weight_random_rand(weight_random_t*,long double);
"""
_weight_random_rand = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_longdouble,
)(('weight_random_rand', mod))

"""
    int weight_random_will_be(weight_random_t*, int, int)
"""
_weight_random_will_be = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_int,
)(('weight_random_will_be', mod))

"""
    void weight_random_destruct(weight_random_t*);
"""
_weight_random_destruct = ctypes.CFUNCTYPE(
    ctypes.c_void_p,
    ctypes.c_void_p,
)(('weight_random_destruct', mod))


def interpolice(ff: list, x: float) -> float:
    az = (ctypes.c_double * len(ff))()  # change to double, double* , double*
    bz = (ctypes.c_double * len(ff))()
    for i in range(len(ff)):
        az[i] = ctypes.c_double(ff[i][0])  # x
        bz[i] = ctypes.c_double(ff[i][1])  # f(x)

    x = ctypes.c_double(x)
    return __interpolice(x, bz, az, len(ff))


class CWeightRandom:
    def __init__(self, data):
        """
            data = [
              [ x0 , y0 ] , - левая точка нуля пораболы
              [ x1 , y1 ] , - пик
              [ x2 , y2 ] - точка после пика через ( x1-x0 )
            ]
            endpoint = mun of second that:
             1. > x0
             2. <= x0 + 86000
        """
        # p = [ x0 , x1 , y1 , y2]
        self.x = data[0][0]
        p = [data[0][0] - self.x, data[1][0] - self.x, data[1][1], data[2][1]]
        mm = [
            [p[0]**2, p[0], 1],
            [p[1]**2, p[1], 1],
            [(2 * p[1] - p[0])**2, (2 * p[1] - p[0]), 1]
        ]
        abc = list(numpy.linalg.solve(mm, [0, p[2], 0]))
        a = abc[0]
        b = abc[1]
        c = abc[2]
        mm = [
            [1.0, -p[2]],
            [1.0, -p[3]]
        ]
        dk = numpy.linalg.solve(mm, [p[2] * p[1], p[3] * (2 * p[1] - p[0])])
        d = dk[0]
        k = dk[1]

        p0 = (ctypes.c_longdouble * 4)()
        for i in range(4):
            p0[i] = ctypes.c_longdouble(p[i])
        az = [a, b, c]
        p1 = (ctypes.c_longdouble * 3)()
        for i in range(len(az)):
            p1[i] = ctypes.c_longdouble(az[i])
        az = [d, k]
        p2 = (ctypes.c_longdouble * 2)()
        for i in range(len(az)):
            p2[i] = ctypes.c_longdouble(az[i])

        self.this = _weight_random_create(p0, p1, p2)

    def random(self, y=1) -> list:
        """
            return random number using spread function
        """
        return (
            [(_weight_random_rand(self.this, random.random()) + self.x) % 86400]
        ) if y <= 1 else (
            [_weight_random_rand(self.this, random.random()) for _ in range(y)]
        )

    def will_be(self, count_now: int, now: int) -> float:
        """
            predict now many obj will be in 24 hours
        """
        return _weight_random_will_be(
            self.this,
            ctypes.c_int(int(count_now)),
            ctypes.c_int(int(now)),
        )

    def destruct(self):
        """
            destructor
        """
        _weight_random_destruct(self.this)


if __name__ == '__main__':
    for i in range(10, 14):
        print(i)
        date = i * 3600
        f = 1.0
        wr = CWeightRandom([
            [date, 0.0],
            [date + (3600 + 600) / f, 3200],
            [date + (2 * 3600) / f, 1850]
        ])
        az = []
        bz = []
        M = 5 * 10**3
        for j in range(M):
            bz.append(j)
            az.append(wr.random())

        import matplotlib.pyplot as plt
        plt.plot(az, bz, 'ro')
        plt.axis([0, 3600 * 24, 0, M])
        plt.show()
        wr.destruct()
