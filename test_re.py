#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Для тестирования регулярных выражений из re


import re


s = '<TD class="not_edit_td"><input type="text" name="var0"	value="Е лена" size="20" border="0" ></TD>'
pattern = r'\bvalue="\b'
result = re.search(pattern, s)
print(result)
# print(dir(result))
