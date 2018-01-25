#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright © 2010 daniel g. siegel <dgsiegel@gnome.org>
#
# Licensed under the GNU General Public License Version 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO:
#  - nest ordered lists into unordered and vice versa

import sys
import os
import re
import string
import codecs


def prefmt_umlauts(t):
  t = re.sub(ur"([ÁÉÍÓÚáéíóú])", r"&\1acute;", t)
  t = re.sub(ur"([ÀÈÌÒÙàèìòù])", r"&\1grave;", t)
  t = re.sub(ur"([ÄËÏÖÜäëïöü])", r"&\1uml;", t)
  t = re.sub(ur"([ÂÊÎÔÛâêîôû])", r"&\1circ;", t)
  t = re.sub(ur"([ÃÕãõ])", r"&\1tilde;", t)
  t = re.sub(ur"&[ÁÀÃÄÂ](\w+;)", r"&A\1", t)
  t = re.sub(ur"&[áàãäâ](\w+;)", r"&a\1", t)
  t = re.sub(ur"&[ÉÈËÊ](\w+;)", r"&E\1", t)
  t = re.sub(ur"&[éèëê](\w+;)", r"&e\1", t)
  t = re.sub(ur"&[ÍÌÏÎ](\w+;)", r"&I\1", t)
  t = re.sub(ur"&[íìïî](\w+;)", r"&i\1", t)
  t = re.sub(ur"&[ÓÒÖÔÕ](\w+;)", r"&O\1", t)
  t = re.sub(ur"&[óòöôõ](\w+;)", r"&o\1", t)
  t = re.sub(ur"&[ÚÙÜÛ](\w+;)", r"&U\1", t)
  t = re.sub(ur"&[úùüû](\w+;)", r"&u\1", t)
  t = re.sub(ur"ß", r"&szlig;", t)
  t = re.sub(ur"Ñ", r"&Ntilde;", t)
  t = re.sub(ur"ñ", r"&ntilde;", t)
  t = re.sub(ur"Ç", r"&Ccedil;", t)
  t = re.sub(ur"ç", r"&ccedil;", t)
  return t


def prefmt(t):
  t = re.sub(r"&(?!#\d+;|#x[\da-fA-F]+;|\w+;)", "&amp;", t)
  t = re.sub("<", "&lt;", t)
  t = re.sub(">", "&gt;", t)
  t = re.sub('"', "&quot;", t)
  t = re.sub('--', "&ndash;", t)
  t = re.sub(r"\\\\", '<br>', t)
  t = re.sub(r"(?ms)\*\*(.*?)\*\*", r"<strong>\1</strong>", t)
  t = re.sub(r"(?ms)(?<!:)//(.+?)(?<!:)//", r"<em>\1</em>", t)
  t = re.sub(r"(?ms)--(.*?)--", r"<del>\1</del>", t)
  t = re.sub(r"(?ms)__(.*?)__", r"<ins>\1</ins>", t)
  t = re.sub(r"(?ms)``(.*?)``", r"<code>\1</code>", t)
  t = re.sub(r"(?ms)~~(.*?)~~", r"<small>\1</small>", t)
  t = re.sub(r"\[(.*?(jpg|jpeg|png|gif|svg))\s?(\S+)\]", r'<a href="\3">[\1]</a>', t)
  t = re.sub(r"\[(.*?)\s?(\S+(jpg|jpeg|png|gif|svg))\]", r'<img src="\2" alt="\1">', t)
  t = re.sub(r"\[(\S+)\]", r'<a href="\1">\1</a>', t)
  t = re.sub(r"\[(.*?)\s?(\S+)\]", r'<a href="\2">\1</a>', t)
  return prefmt_umlauts(t)

def prefmt_simple(t):
  t = re.sub("&", "&amp;", t)
  t = re.sub("<", "&lt;", t)
  t = re.sub(">", "&gt;", t)
  t = re.sub('"', "&quot;", t)
  return t


def tag(t, open=True, self=False):
  if self:
    return "<" + t + ">"
  elif open:
    return "<" + t + ">"
  elif not open:
    return "</" + t + ">"
  return


def spacer(deep):
  return " " * (deep + 1)


def parse(text):
  paras = re.split("\n\n+|\n$", text)

  for i in range(len(paras)):

    if paras[i] == "":
      continue
    elif paras[i].startswith("="):
      if paras[i].startswith("====== "):
        t = "h6"
      elif paras[i].startswith("===== "):
        t = "h5"
      elif paras[i].startswith("==== "):
        t = "h4"
      elif paras[i].startswith("=== "):
        t = "h3"
      elif paras[i].startswith("== "):
        t = "h2"
      elif paras[i].startswith("= "):
        t = "h1"
      else:
        t = "h6"
      paras[i] = re.sub(r"^=+ ", tag(t), re.sub(" =+$", tag(t, open=False), prefmt(paras[i])))
    elif paras[i].startswith("- ") or paras[i].startswith("+ "):

      list = []
      listitems = re.findall("^([ \t]*[-\+]) (.+?)$(?=\n^([ \t]*[-\+])|\n*\Z)", paras[i], re.MULTILINE | re.DOTALL)

      if paras[i].startswith("- "):
        pre_tag = tag("ul")
        post_tag = tag("ul", open=False)
      else:
        pre_tag = tag("ol")
        post_tag = tag("ol", open=False)

      list.append(pre_tag)
      for item in listitems:
        currentlen = len(item[0])
        nextlen = len(item[2])

        if currentlen == nextlen:
          list.append(spacer(currentlen) + tag("li") + prefmt(item[1]) + tag("li", open=False))
        elif currentlen < nextlen:
          list.append(spacer(currentlen) + tag("li") + prefmt(item[1]))
          list.append(spacer(currentlen) + pre_tag)
        else:
          list.append(spacer(currentlen) + tag("li") + prefmt(item[1]) + tag("li", open=False))
          while (currentlen - nextlen) >= 2:
            currentlen = currentlen - 2
            list.append(spacer(currentlen) + post_tag)
            list.append(spacer(currentlen) + tag("li", open=False))

      list.append(post_tag)
      paras[i] = '\n'.join(list)
    elif paras[i].startswith("  ") and paras[i].split("\n")[-1].startswith("  --"):
      parts = paras[i].split("\n  -- ")
      cite =  tag("cite") + prefmt(parts[1]) + tag("cite", open=False) + "\n"
      paras[i] = tag("blockquote") + "\n" + "\n".join([tag("p") + "\n" + prefmt(p) + "\n" + tag("p", open=False) for p in parts[0].split("\n  \n")]) + "\n" + cite + tag("blockquote", open=False)
    elif paras[i].startswith("  "):
      paras[i] = tag("blockquote") + "\n" + "\n".join([tag("p") + "\n" + prefmt(p) + "\n" + tag("p", open=False) for p in paras[i].split("\n  \n")]) + "\n" + tag("blockquote", open=False)
    elif paras[i].startswith("---"):
      paras[i] = re.sub(r"^---\n", tag("pre") + tag("code"), re.sub("---$", tag("code", open=False) + tag("pre", open=False), prefmt_simple(paras[i])))
    elif paras[i].startswith("."):
      cls = paras[i].split()[0][1:]
      paras[i] = re.sub(r"^\.[\w_-]+ ", tag("div class=\"" + cls + "\"") + "\n", re.sub("$", "\n" + tag("div", open=False), prefmt(paras[i])))
    elif paras[i].startswith("<"):
      continue
    elif paras[i].startswith("#"):
      paras[i] = ""
    else:
      paras[i] = tag("p") + "\n" + prefmt(paras[i]) + "\n" + tag("p", open=False)

  paras = [p for p in paras if p != ""]
  return "\n\n".join(paras)


if len(sys.argv) > 1:
  path = sys.argv[1]
else:
  print "Usage: %s [file]" % sys.argv[0]
  sys.exit(1)

if not path or not os.path.exists(path):
  print "Usage: %s [file]" % sys.argv[0]
  sys.exit(1)

f = codecs.open(path, "r", "utf-8")
lines = f.read()
f.close()

p = parse(lines).encode("utf-8")
print p
