# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Erebos Labs
"""Rigid regular polygons and their formal no-slip, level-axle roads.

Length unit is apothem a; angle phi is clockwise in radians.
This is geometry/kinematics, not a friction/contact-force simulator.
"""
from math import asinh, cos, cosh, floor, isfinite, pi, sin, sinh, sqrt, tan


def parameters(n=4, a=1.0):
    if not isinstance(n, int) or isinstance(n, bool) or n < 3:
        raise ValueError('n must be an integer >= 3')
    if not isfinite(a) or a <= 0:
        raise ValueError('a must be positive and finite')
    alpha = pi / n
    b = a * asinh(tan(alpha))
    return alpha, b, 2 * b


def phase(phi, n=4):
    if not isfinite(phi):
        raise ValueError('phi must be finite')
    alpha, _, _ = parameters(n)
    k = floor((phi + alpha) / (2 * alpha))
    return k, phi - k * 2 * alpha


def radius(phi, n=4, a=1.0):
    parameters(n, a)
    _, delta = phase(phi, n)
    return a / cos(delta)


def axle_x(phi, n=4, a=1.0):
    _, _, period = parameters(n, a)
    k, delta = phase(phi, n)
    return k * period + a * asinh(tan(delta))


def road_y(x, n=4, a=1.0):
    _, b, period = parameters(n, a)
    k = floor((x + b) / period)
    return -a * cosh((x - k * period) / a)


def turn(point, phi):
    x, y = point
    return (x * cos(phi) + y * sin(phi), -x * sin(phi) + y * cos(phi))


def material_point(theta, n=4, a=1.0):
    r = radius(theta, n, a)
    return r * sin(theta), -r * cos(theta)


def move(point, phi, n=4, a=1.0):
    x, y = turn(point, phi)
    return x + axle_x(phi, n, a), y


def vertices(phi, n=4, a=1.0):
    alpha, _, _ = parameters(n, a)
    r = a / cos(alpha)
    return [move((r * sin((2*j+1)*alpha), -r * cos((2*j+1)*alpha)), phi, n, a)
            for j in range(n)]


def edge_clearance(p, q, n=4, a=1.0):
    """Minimum vertical wheel-minus-road gap on a continuous segment.

    Each road arch is concave, so gap along a nonvertical straight edge
    is convex within that arch. Evaluate its endpoints and sole stationary
    point, splitting at every road cusp. No boundary discretization here.
    Returns (gap, location, edge parameter).
    """
    _, b, period = parameters(n, a)
    x0, y0 = p
    dx, dy = q[0] - x0, q[1] - y0
    samples = [0.0, 1.0]
    if abs(dx) > 1e-14 * a:
        lo, hi = sorted((x0, q[0]))
        first = floor((lo - b) / period) - 1
        last = floor((hi - b) / period) + 1
        for k in range(first, last + 1):
            s = (k * period + b - x0) / dx
            if 0 < s < 1:
                samples.append(s)
        cuts = sorted(samples)
        for left, right in zip(cuts, cuts[1:]):
            xm = x0 + dx * ((left + right) / 2)
            k = floor((xm + b) / period)
            xstar = k * period - a * asinh(dy / dx)
            s = (xstar - x0) / dx
            if left < s < right:
                samples.append(s)
    best = None
    for s in samples:
        x, y = x0 + dx*s, y0 + dy*s
        gap = y - road_y(x, n, a)
        if best is None or gap < best[0]:
            best = gap, (x, y), s
    return best


def polygon_clearance(phi, n=4, a=1.0):
    v = vertices(phi, n, a)
    gaps = [(*edge_clearance(v[j], v[(j+1) % n], n, a), j) for j in range(n)]
    return min(gaps, key=lambda item: item[0])


def free_speed(phi, n=4, a=1.0, inertia_per_mass=None, energy_per_mass=0.5):
    """Energy-conserving formal speed, conditional on maintained contact.

    K/m = .5 * (1 + (I/m)/r**2) * v**2. For a uniform filled regular
    polygon, I/m = a**2/6 * (3 + tan(pi/n)**2).
    No rolling resistance, drive, friction coefficient, or force feasibility.
    """
    alpha, _, _ = parameters(n, a)
    if inertia_per_mass is None:
        inertia_per_mass = a*a * (3 + tan(alpha)**2) / 6
    r = radius(phi, n, a)
    return sqrt(2 * energy_per_mass / (1 + inertia_per_mass/(r*r)))
