# Sources and third-party notices

This is an AI-assisted, independently implemented numerical illustration of established mathematical ideas. It is not a claim of discovering catenary roads, no-slip kinematics or rolling-wheel dynamics. The diagrams are newly rendered from the included code rather than copied from source publications. No author endorsement is implied.

## Rolling-wheel mathematics

- Antonin Slavik and Stan Wagon, *A Minimalist Approach to Rolling Wheels*, arXiv:2604.03749v3, 14 May 2026: https://arxiv.org/abs/2604.03749v3 . The no-slip road construction, triangle collision and equal-arc-length counterexample informed the implementation. Sections 2, 3.1 and 4 are the main references. The paper is a preprint. Its page-3 negative inverse-derivative sign conflicts with the positive theorem on page 2; this implementation uses the independently derived positive relation. The source PDF is not distributed. The arXiv non-exclusive distribution licence grants arXiv distribution rights; this package does not purport to sublicense the paper.
- Leon Hall, *Roads and Wheels*, author explanation: https://web.mst.edu/_disabled/lmhall/Personal/RoadsWheels/roads.html . It defines smooth rolling as a level axle and describes matching catenary roads. The original 1992 Hall/Wagon article was identified in references but not read for this reconstruction.
- OpenStax, *University Physics Volume 1*, section 11.1 Rolling Motion: https://openstax.org/books/university-physics-volume-1/pages/11-1-rolling-motion . Background for general energy conservation, Newton's equations and static-friction conditions; the variable-contact-radius calculation here is separately derived. No textbook text or illustration is copied into this package.

## Tooling and typography

Python and Pillow are external execution requirements, not bundled code. Pillow uses the MIT-CMU licence: https://pillow.readthedocs.io/en/stable/about.html#license . The figure code calls `ImageFont.load_default(size=...)`, documented by Pillow as using a bundled Aileron Regular face with limited character coverage when FreeType is available: https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.load_default . No font binary or font source is redistributed. The font author's Aileron page states “No Rights Reserved”: https://dotcolon.net/fonts/aileron/ . This notice does not apply a different licence to that font.

All third-party copyrights and licence terms remain with their respective holders. Mathematical model descriptions, citations and links are not a grant of rights over the original publications or runtime dependencies.
