# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Erebos Labs
"""Conditional free rolling of one uniform square lamina, with a=m=g=1.

A point-contact idealization; no air drag, bearing load, rider, axle force,
rolling resistance, deformation or cusp impact law. One-sided force
requirements are computed on smooth portions, not a frictional simulation.
"""
from pathlib import Path
from math import cos, pi, sin, sqrt, tan
import json

OUT=Path(__file__).resolve().parent/'output'
alpha=pi/4
kappa=2/3  # I/m = mean of x*x+y*y over [-1,1]^2.

def rates(delta, omega):
    r=1/cos(delta)
    rp=r*tan(delta)
    return -r*rp*omega/(kappa+r*r), 1/omega

# Independent ODE in rotation angle. Integrate a single face with one-sided
# derivatives at both ends rather than crossing a discontinuity unnoticed.
def run(steps):
    h=2*alpha/steps
    omega=1.0
    elapsed=0.0
    E0=(kappa+2)/2
    max_energy_error=0
    max_omega_error=0
    for i in range(steps):
        delta=-alpha+i*h
        k1,t1=rates(delta,omega)
        k2,t2=rates(delta+h/2,omega+h*k1/2)
        k3,t3=rates(delta+h/2,omega+h*k2/2)
        k4,t4=rates(delta+h,omega+h*k3)
        omega+=h*(k1+2*k2+2*k3+k4)/6
        elapsed+=h*(t1+2*t2+2*t3+t4)/6
        r=1/cos(delta+h)
        E=(kappa+r*r)*omega*omega/2
        max_energy_error=max(max_energy_error,abs(E-E0))
        expected=sqrt(2*E0/(kappa+r*r))
        max_omega_error=max(max_omega_error,abs(omega-expected))
    return {'steps':steps,'face_time':elapsed,'final_omega':omega,
            'max_energy_error':max_energy_error,'max_omega_error':max_omega_error}

# Derive reaction from Newton's equations: Fx=m*ax, Fy=mg, and
# I*omega_dot=-r*Fx (clockwise-positive omega). With v=r*omega:
# ax = kappa*r'*omega**2/(kappa+r**2).
# Road slope = -tan(delta), so N=cos(delta)+ax*sin(delta),
# tangential reaction T=ax*cos(delta)-sin(delta), both per unit mass.
def force_sample(delta,E):
    r=1/cos(delta)
    rp=r*tan(delta)
    omega=sqrt(2*E/(kappa+r*r))
    omega_dot=-r*rp*omega*omega/(kappa+r*r)
    ax=kappa*rp*omega*omega/(kappa+r*r)
    N=cos(delta)+ax*sin(delta)
    T=ax*cos(delta)-sin(delta)
    return {'delta':delta,'normal':N,'tangent':T,'mu_required':abs(T)/N,
            'torque_residual':kappa*omega_dot+r*ax,
            'constraint_residual':ax-(rp*omega*omega+r*omega_dot)}

force_checks=[]
for E in (0.01,0.5,4/3):
    samples=[force_sample(-alpha+2*alpha*i/10000,E) for i in range(10001)]
    worst=max(samples,key=lambda s:s['mu_required'])
    force_checks.append({'energy_per_mass_in_units_ag':E,
                         'min_normal_per_mass_in_units_g':min(s['normal'] for s in samples),
                         'max_required_mu':worst['mu_required'],'worst_delta':worst['delta'],
                         'torque_residual':max(abs(s['torque_residual']) for s in samples),
                         'constraint_residual':max(abs(s['constraint_residual']) for s in samples)})
result={'assumptions':__doc__.strip(),'square_I_over_ma2':kappa,
        'ode_runs':[run(s) for s in (32,64,128,256)],'one_sided_force_checks':force_checks,
        'status':'PASS'}
assert result['ode_runs'][-1]['max_energy_error']<1e-9
assert result['ode_runs'][-1]['max_omega_error']<1e-9
assert all(s['min_normal_per_mass_in_units_g']>0 for s in force_checks)
assert all(s['torque_residual']<1e-12 and s['constraint_residual']<1e-12 for s in force_checks)
(OUT/'dynamics-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
