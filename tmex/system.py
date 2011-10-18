# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import sys, platform

ARCHITECTURE_BITS = 0
# arch_bits should be either '32bit' or '64bit', arch_linker should be 'WindowsPE' on Windows.
(arch_bits, arch_linker) = platform.architecture()
architectures = {'32bit': 32, '64bit': 64}
if arch_bits in architectures:
    ARCHITECTURE_BITS = architectures[arch_bits]

ISPYTHON3 = sys.version_info[0] == 3

def iteritems(d):
    """
    Convenience function to handle items iterator for Python 2 and Python 3.
    """
    if ISPYTHON3:
        return d.items()
    else:
        return d.iteritems()

def itervalues(d):
    """
    Convenience function to handle value iterator for Python 2 and Python 3.
    """
    if ISPYTHON3:
        return d.values()
    else:
        return d.itervalues()