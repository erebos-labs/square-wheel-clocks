# Executed validation and limits

The initial and clean portable versions were checked with existing Python 3.14.7 and Pillow 12.2.0, without installing dependencies. The publication copy is checked again before release. Only the recorded checks below support the claims.

- `probe.py`: independent quadrature, finite differences of frozen material-point velocity, contact identity, 2,001 poses for each of n=3,4,5,6,8,12, and 300 random continuous-edge-oracle comparisons against 4,001 samples per segment (seed 1960). Final status PASS; square contact residual about 1.33e-15; triangle sampled penetration about 0.095216 apothems. Pose sampling is not an all-angle proof.
- `dynamics.py`: independent angle-domain ODE convergence at 32/64/128/256 steps. Finest energy residual about 1.92e-11 and angular-speed error about 9.12e-12. One-sided force requirements for an isolated uniform square at three energy values; no general frictional contact simulation or cusp impact law.
- `animation_check.py`: all 240 poses across two clocks checked; inverse position error about 4.44e-16, no penetration beyond roundoff, monotone rotation for constant forward speed.
- `figures.py`: two PNGs, four-frame montage and 120-frame GIF regenerated. All GIF frames decoded; 7,200 ms total loop duration. Both PNGs and montage visually reviewed. Continuous playback was not watched in a browser.
- `verify_release.py`: bounded package checks for private identifiers/paths and common credential patterns, syntax, source-PDF/font/bytecode exclusions, numerical output consistency, and manifest/archive validation. This is a publication hygiene check, not a vulnerability assessment or guarantee that every possible secret pattern is detectable.

The independent all-pose square-clearance argument is in `PROOF.md`. It is a written geometric argument, not a formally verified proof. The free-square speed result assumes maintained lossless no-slip contact. No physical wheel, real vehicle, physical phone or accessibility evaluation was tested.

Two development test defects were corrected: `1e-5` versus the actual formatted key `1e-05`, and an arbitrary penetration threshold of 0.1 when the actual penetration was about 0.095216. The corrections did not alter numerical outputs.
