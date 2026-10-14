# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Erebos Labs
"""Verify inverse clock mapping and whole-wheel clearance of animation poses."""
from pathlib import Path
import math
import json
from model import axle_x, parameters, polygon_clearance
alpha,b,L=parameters()
errors=[];gaps=[];phis=[]
for i in range(120):
    u=i/119
    x=2*L*u
    k=math.floor((x+b)/L)
    phi=2*alpha*k+math.atan(math.sinh(x-k*L))
    errors.append(abs(axle_x(phi)-x));phis.append(phi)
    gaps.extend((polygon_clearance(phi)[0],polygon_clearance(math.pi*u)[0]))
assert max(errors)<1e-12 and min(gaps)>-1e-12
assert all(p<q for p,q in zip(phis,phis[1:]))
result={'frames_per_clock':120,'clocks':2,'inverse_position_max_error':max(errors),'minimum_gap_all_animation_poses':min(gaps),'constant_v_rotation_monotone':True,'status':'PASS'}
out=Path(__file__).resolve().parent/'output'
(out/'animation-model-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
