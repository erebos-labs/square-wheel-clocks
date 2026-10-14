# Why the square clears the road

This is an independent geometric reconstruction using concavity and tangent lines. It establishes nonpenetration, with contact permitted; it does not establish dynamic contact feasibility or perceived comfort.

Set the square apothem to 1, use clockwise angle `phi`, and write `b = asinh(1)`. The axle is `(x,0)`, where `x = asinh(tan(phi))` on a face. The road consists of translated copies of `y = -cosh(X)` on `[-b,b]`, with period `2b`.

By symmetry it suffices to consider `0 <= phi <= pi/4`. Write `s = sin(phi)`, `c = cos(phi)`.

The current bottom face is tangent to the middle arch. A concave arch lies below every tangent line, and the square's interior lies above its bottom face. Thus wheel points above the middle arch cannot penetrate it.

The right neighboring arch lies below its tangent at the left cusp:

```
y = X - b - sqrt(2)
```

The minimum of `y - X` over the rotated square is `-2c - x`, attained at the vertex initially `(1,-1)`. Its tangent clearance is

```
G_right(phi) = sqrt(2) + b - x - 2c
G_right(pi/4) = 0
G_right'(phi) = -sec(phi) + 2sin(phi)
             = (sin(2phi) - 1) / cos(phi) <= 0
```

Therefore `G_right >= 0` over the whole interval, and the entire square clears that neighboring arch.

The left neighbor's tangent is `y = -X - b - sqrt(2)`. The minimum of `y + X` over the square is `x - 2c`, giving clearance

```
G_left = sqrt(2) + b + x - 2c
       >= sqrt(2) + b - 2 > 0
```

Finally, the square's horizontal extent is within `[-sqrt(2), b+sqrt(2)]`, which is inside `[-3b,3b]`. Those three arches exhaust the possible intersections. Reflection and the road/wheel periodicity cover all remaining poses.

For the general road-construction framework and a separate square-clearance proof, see Antonin Slavik & Stan Wagon, *A Minimalist Approach to Rolling Wheels*, https://arxiv.org/abs/2604.03749v3 . The included figures and code are numerical reconstructions rather than copies of the paper's figures.
