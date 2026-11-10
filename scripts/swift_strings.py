"""Lex Swift strings and balanced interpolation expressions without rewriting model data."""
def skip_string(s, i):
    triple = s.startswith('"""', i)
    delimiter = '"""' if triple else '"'
    j = i + len(delimiter)
    while j < len(s):
        if s.startswith('\\(', j):
            j = end_group(s, j+1) + 1
        elif s[j] == '\\': j += 2
        elif s.startswith(delimiter, j): return j + len(delimiter)
        else: j += 1
    return j

def end_group(s, i):
    closing = {'(':')','[':']','{':'}'}[s[i]]
    j = i+1
    while j < len(s):
        if s[j] == '"': j = skip_string(s,j)
        elif s[j] in '([{': j = end_group(s,j)+1
        elif s[j] == closing: return j
        else: j += 1
    return j

def first_argument(s, i):
    j = i+1
    while j < len(s):
        if s[j] == '"': j = skip_string(s,j)
        elif s[j] in '([{': j = end_group(s,j)+1
        elif s[j] in ',)': return i+1,j
        else: j += 1
    return i+1,j
