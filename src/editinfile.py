#!/usr/bin/env python
# coding=utf-8

import sys
import config



def editinfile(pqr, dx=None):
    sdie = config.CONFIG_DEFAULT_SDIE

    in_content = """
read
    mol pqr %s
end
elec 
    mg-auto
    dime 161 193 129
    cglen 115.1257 125.4175 81.6646
    fglen 87.7210 93.7750 68.0380
    cgcent mol 1
    fgcent mol 1
    mol 1
    lpbe
    bcfl sdh
    pdie 2.0000
    sdie %s
    srfm smol
    chgm spl2
    sdens 10.00
    srad 1.40
    swin 0.30
    temp 298.15
    write pot dx %s
end
quit
"""

    infile = pqr[:-4] + ".in"
    dx = infile[:-3] if dx is None else dx[:-3]
    content = in_content % (pqr, sdie, dx)
    f = open(infile, 'w')
    f.write(content)
    f.close()

    return infile, dx + '.dx'


if __name__ == "__main__":
    import sys

    print editinfile(sys.argv[1])
