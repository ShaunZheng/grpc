#!/usr/bin/env python2.7

# Copyright 2015, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import hashlib
import itertools
import os
import sys

# configuration: a list of either strings or 2-tuples of strings
# a single string represents a static grpc_mdstr
# a 2-tuple represents a static grpc_mdelem (and appropriate grpc_mdstrs will
# also be created)

CONFIG = [
    'grpc-timeout',
    ':path',
    'grpc-encoding',
    'grpc-accept-encoding',
    'user-agent',
    ':authority',
    'host',
    'grpc-message',
    'grpc-status',
    '',
    ('grpc-status', '0'),
    ('te', 'trailers'),
    (':method', 'POST'),
    (':status', '200'),
    (':status', '404'),
    (':scheme', 'http'),
    (':scheme', 'https'),
    (':scheme', 'grpc'),
    (':authority', ''),
    (':method', 'GET'),
    (':path', '/'),
    (':path', '/index.html'),
    (':status', '204'),
    (':status', '206'),
    (':status', '304'),
    (':status', '400'),
    (':status', '500'),
    ('accept-charset', ''),
    ('accept-encoding', ''),
    ('accept-encoding', 'gzip, deflate'),
    ('accept-language', ''),
    ('accept-ranges', ''),
    ('accept', ''),
    ('access-control-allow-origin', ''),
    ('age', ''),
    ('allow', ''),
    ('authorization', ''),
    ('cache-control', ''),
    ('content-disposition', ''),
    ('content-encoding', ''),
    ('content-language', ''),
    ('content-length', ''),
    ('content-location', ''),
    ('content-range', ''),
    ('content-type', ''),
    ('cookie', ''),
    ('date', ''),
    ('etag', ''),
    ('expect', ''),
    ('expires', ''),
    ('from', ''),
    ('host', ''),
    ('if-match', ''),
    ('if-modified-since', ''),
    ('if-none-match', ''),
    ('if-range', ''),
    ('if-unmodified-since', ''),
    ('last-modified', ''),
    ('link', ''),
    ('location', ''),
    ('max-forwards', ''),
    ('proxy-authenticate', ''),
    ('proxy-authorization', ''),
    ('range', ''),
    ('referer', ''),
    ('refresh', ''),
    ('retry-after', ''),
    ('server', ''),
    ('set-cookie', ''),
    ('strict-transport-security', ''),
    ('transfer-encoding', ''),
    ('user-agent', ''),
    ('vary', ''),
    ('via', ''),
    ('www-authenticate', ''),
]

# utility: mangle the name of a config
def mangle(elem):
  xl = {
      '-': '_',
      ':': '',
      '/': 'slash',
      '.': 'dot',
      ',': 'comma',
      ' ': '_',
  }
  def m0(x):
    if not x: return 'empty'
    r = ''
    for c in x:
      put = xl.get(c, c.lower())
      if not put: continue
      last_is_underscore = r[-1] == '_' if r else True
      if last_is_underscore and put == '_': continue
      elif len(put) > 1:
        if not last_is_underscore: r += '_'
        r += put
        r += '_'
      else:
        r += put
    if r[-1] == '_': r = r[:-1]
    return r
  if isinstance(elem, tuple):
    return 'grpc_mdelem_%s_%s' % (m0(elem[0]), m0(elem[1]))
  else:
    return 'grpc_mdstr_%s' % (m0(elem))

# utility: generate some hash value for a string
def fake_hash(elem):
  return hashlib.md5(elem).hexdigest()[0:8]

# utility: print a big comment block into a set of files
def put_banner(files, banner):
  for f in files:
    print >>f, '/*'
    for line in banner:
      print >>f, ' * %s' % line
    print >>f, ' */'
    print >>f

# build a list of all the strings we need
all_strs = set()
all_elems = set()
for elem in CONFIG:
  if isinstance(elem, tuple):
    all_strs.add(elem[0])
    all_strs.add(elem[1])
    all_elems.add(elem)
  else:
    all_strs.add(elem)
all_strs = sorted(list(all_strs), key=mangle)
all_elems = sorted(list(all_elems), key=mangle)

# output configuration
args = sys.argv[1:]
H = None
C = None
if args:
  if 'header' in args:
    H = sys.stdout
  else:
    H = open('/dev/null', 'w')
  if 'source' in args:
    C = sys.stdout
  else:
    C = open('/dev/null', 'w')
else:
  H = open(os.path.join(
      os.path.dirname(sys.argv[0]), '../../../src/core/transport/static_metadata.h'), 'w')
  C = open(os.path.join(
      os.path.dirname(sys.argv[0]), '../../../src/core/transport/static_metadata.c'), 'w')

# copy-paste copyright notice from this file
with open(sys.argv[0]) as my_source:
  copyright = []
  for line in my_source:
    if line[0] != '#': break
  for line in my_source:
    if line[0] == '#':
      copyright.append(line)
      break
  for line in my_source:
    if line[0] != '#':
      break
    copyright.append(line)
  put_banner([H,C], [line[1:].strip() for line in copyright])

put_banner([H,C],
"""WARNING: Auto-generated code.

To make changes to this file, change tools/codegen/core/gen_static_metadata.py,
and then re-run it.
""".splitlines())

print >>H, '#ifndef GRPC_INTERNAL_CORE_TRANSPORT_STATIC_METADATA_H'
print >>H, '#define GRPC_INTERNAL_CORE_TRANSPORT_STATIC_METADATA_H'
print >>H
print >>H, '#include "src/core/transport/metadata.h"'
print >>H

print >>C, '#include "src/core/transport/static_metadata.h"'
print >>C

print >>H, '#define GRPC_STATIC_MDSTR_COUNT %d' % len(all_strs)
print >>H, 'extern grpc_mdstr grpc_static_mdstr_table[GRPC_STATIC_MDSTR_COUNT];'
for i, elem in enumerate(all_strs):
  print >>H, '/* "%s" */' % elem
  print >>H, '#define %s (&grpc_static_mdstr_table[%d])' % (mangle(elem).upper(), i)
print >>H
print >>C, 'grpc_mdstr grpc_static_mdstr_table[GRPC_STATIC_MDSTR_COUNT];'
print >>C

print >>H, '#define GRPC_STATIC_MDELEM_COUNT %d' % len(all_elems)
print >>H, 'extern grpc_mdelem grpc_static_mdelem_table[GRPC_STATIC_MDELEM_COUNT];'
for i, elem in enumerate(all_elems):
  print >>H, '/* "%s": "%s" */' % elem
  print >>H, '#define %s (&grpc_static_mdelem_table[%d])' % (mangle(elem).upper(), i)
print >>H
print >>C, 'grpc_mdelem grpc_static_mdelem_table[GRPC_STATIC_MDELEM_COUNT];'
print >>C

def str_idx(s):
  for i, s2 in enumerate(all_strs):
    if s == s2:
      return i

print >>H, 'const gpr_uint8 grpc_static_metadata_elem_indices[GRPC_STATIC_MDELEM_COUNT*2];'
print >>C, 'const gpr_uint8 grpc_static_metadata_elem_indices[GRPC_STATIC_MDELEM_COUNT*2] = {'
print >>C, ','.join('%d' % str_idx(x) for x in itertools.chain.from_iterable([a,b] for a, b in all_elems))
print >>C, '};'
print >>C

print >>H, 'const char *const grpc_static_metadata_strings[GRPC_STATIC_MDSTR_COUNT];'
print >>C, 'const char *const grpc_static_metadata_strings[GRPC_STATIC_MDSTR_COUNT] = {'
print >>C, '%s' % ',\n'.join('  "%s"' % s for s in all_strs)
print >>C, '};'
print >>C

print >>H, '#endif /* GRPC_INTERNAL_CORE_TRANSPORT_STATIC_METADATA_H */'

H.close()
C.close()

