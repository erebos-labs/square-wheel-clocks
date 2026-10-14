# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Erebos Labs
"""Bounded, reproducible numerical checks; all results are model observations."""
from pathlib import Path
import csv
import json
from math import cos, hypot, pi, sin, sqrt, tan
import random
from model import (axle_x, edge_clearance, free_speed, material_point, move,
                   parameters, polygon_clearance, radius, road_y, vertices)

OUT = Path(__file__).resolve().parent / 'output'
OUT.mkdir(exist_ok=True)
checks = {}

# Independent RK4 quadrature of x'=r, rather than evaluating analytic x.
# Integrate exactly one face, with endpoints at the cusps.
def integrate_face(n, steps):
    alpha, b, _ = parameters(n)
    h = 2*alpha/steps
    x = -b
    for i in range(steps):
        p = -alpha + i*h
        x += h*(radius(p,n) + 4*radius(p+h/2,n) + radius(p+h,n))/6
    return abs(x-b)
checks['quadrature'] = {str(n): {str(s): integrate_face(n,s) for s in (32,64,128,256)}
                        for n in (3,4,5,8,12)}
assert all(v['256'] < 2e-8 for v in checks['quadrature'].values())

# A frozen material point is differentiated; differentiating the moving
# contact label would give the velocity of successive road locations instead.
fd = {}
for h in (1e-3,1e-4,1e-5,1e-6):
    interior = []
    cusp = []
    for i in range(1001):
        phi = -pi/4 + (pi/2)*i/1000
        p = material_point(phi)
        lo, hi = move(p,phi-h), move(p,phi+h)
        err = hypot((hi[0]-lo[0])/(2*h), (hi[1]-lo[1])/(2*h))
        (cusp if i in (0,1000) else interior).append(err)
    fd[str(h)] = {'interior_max':max(interior),'cusp_max':max(cusp)}
checks['frozen_contact_velocity'] = fd
assert fd[str(1e-5)]['interior_max'] < 1e-8
assert fd[str(1e-6)]['cusp_max'] < 1e-6

# Independent identity: contact point coincides with the road directly
# beneath the axle. This says nothing about the rest of the wheel.
contact_error = 0
for n in (3,4,5,6,8,12):
    for i in range(1001):
        phi = 2*pi*i/1000
        px, py = move(material_point(phi,n), phi,n)
        x = axle_x(phi,n)
        contact_error = max(contact_error,abs(px-x),abs(py-road_y(x,n)))
checks['contact_identity_max_error'] = contact_error
assert contact_error < 1e-12

# Continuous-edge gap oracle; only the pose angle is sampled.
clearance = {}
for n in (3,4,5,6,8,12):
    alpha,_,_ = parameters(n)
    values = []
    for i in range(2001):
        phi = -alpha+2*alpha*i/2000
        gap,point,s,edge = polygon_clearance(phi,n)
        values.append((gap,phi,point,s,edge))
    minimum = min(values,key=lambda p:p[0])
    clearance[str(n)] = {'poses':len(values),'minimum_gap':minimum[0],
                        'phi':minimum[1],'point':minimum[2],
                        'edge_parameter':minimum[3],'edge':minimum[4]}
checks['continuous_edge_clearance'] = clearance
assert clearance['3']['minimum_gap'] < -1e-6
assert all(v['minimum_gap'] > -1e-12 for k,v in clearance.items() if k!='3')

# Cross-check oracle against dense, independent samples on arbitrary
# segments, including verticals. Dense minimum must bound exact from above.
rng = random.Random(1960)
max_grid_excess = 0
for case in range(300):
    n = rng.choice((3,4,5,6,8,12))
    p = (rng.uniform(-4,4),rng.uniform(-2,2))
    q = (p[0] if case%20==0 else rng.uniform(-4,4),rng.uniform(-2,2))
    exact = edge_clearance(p,q,n)[0]
    dense = min((p[1]+(q[1]-p[1])*i/4000)-road_y(p[0]+(q[0]-p[0])*i/4000,n)
                for i in range(4001))
    assert exact <= dense + 1e-12,(case,exact,dense)
    max_grid_excess=max(max_grid_excess,dense-exact)
    assert dense-exact < 0.004,(case,exact,dense)
checks['edge_oracle_cross_check'] = {'segments':300,'samples_per_segment':4001,
                                   'seed':1960,'max_dense_minus_exact':max_grid_excess}

# Speed and acceleration, with omega=1 and a=1.
alpha,b,L=parameters(4)
checks['square_metrics']={
    'apothem':1,'side':2,'arch_half_width':b,'road_period':L,
    'arch_drop':sqrt(2)-1,'road_arc_length_per_arch':2,
    'flat_road_axle_bob':sqrt(2)-1,
    'constant_omega_min_speed':1,'constant_omega_max_speed':sqrt(2),
    'constant_omega_mean_speed':L/(2*alpha),
    'constant_omega_acceleration_left_of_cusp':sqrt(2),
    'constant_omega_acceleration_right_of_cusp':-sqrt(2),
    'constant_v_min_omega':1/sqrt(2),'constant_v_max_omega':1,
    'uniform_lamina_free_min_speed':free_speed(0),
    'uniform_lamina_free_max_speed':free_speed(alpha),
    'uniform_lamina_free_speed_ratio':free_speed(alpha)/free_speed(0)}
assert abs(checks['square_metrics']['uniform_lamina_free_speed_ratio']-sqrt(5/4))<1e-12

# Counterexample from section 4, independently evaluate frozen point's
# velocity under phi=2*theta and tau(phi)=2*tan(phi/2).
counter = []
for theta in (0.1,0.25,0.5,0.7):
    p = (tan(theta),-1)
    phi = 2*theta
    xp = p[0]*cos(phi)+p[1]*sin(phi)
    yp = -p[0]*sin(phi)+p[1]*cos(phi)
    C = (xp+2*tan(phi/2),yp)
    v = (yp+1/(cos(phi/2)**2),-xp)
    assert abs(C[0]-p[0])<1e-12 and abs(C[1]+1)<1e-12
    assert hypot(*v)>0.1
    counter.append({'theta':theta,'wheel_arc':tan(theta),'road_arc':C[0],
                    'contact':C,'velocity_per_unit_rotation':v,'speed':hypot(*v)})
checks['equal_arcs_counterexample']=counter

# Flat support height; polygon would require vertical motion on a flat road.
rows=[]
for i in range(1001):
    phi=-alpha+2*alpha*i/1000
    v=vertices(phi)
    r=radius(phi)
    rows.append({'phi':phi,'axle_x':axle_x(phi),'road_y_under_axle':road_y(axle_x(phi)),
                 'constant_omega_speed':r,'constant_omega_acceleration':r*tan(phi),
                 'constant_v_omega':1/r,'flat_road_axle_height':-min(y for x,y in v),
                 'free_uniform_lamina_speed':free_speed(phi)})
with (OUT/'square-phase-sweep.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
checks['status']='PASS'
checks['limits']=['Geometry and kinematics only; no empirical ride or contact-force simulation.',
                  'Clearance is continuous along edges but sampled at 2001 pose angles per polygon.',
                  'Finite differences at cusps converge more slowly because acceleration has a jump.',
                  'Free-speed calculation assumes energy conservation and maintained no-slip contact.']
(OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
