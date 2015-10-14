# This file entirely ripped from the excellent ERPpeek
# https://github.com/tinyerp/erppeek/blob/master/erppeek.py
import re
import _ast

int_types = int, float
DOMAIN_OPERATORS = frozenset('!|&')
# Supported operators are:
#   =, !=, >, >=, <, <=, like, ilike, in, not like, not ilike, not in,
#   child_of, =like, =ilike, =?
_term_re = re.compile(
    '([\w._]+)\s*'  '(=(?:like|ilike|\?)|[<>]=?|!?=(?!=)'
    '|(?<= )(?:like|ilike|in|not like|not ilike|not in|child_of))'  '\s*(.*)')

# Simplified ast.literal_eval which does not parse operators
def _convert(node, _consts={'None': None, 'True': True, 'False': False}):
    if isinstance(node, _ast.Str):
        return node.s
    if isinstance(node, _ast.Num):
        return node.n
    if isinstance(node, _ast.Tuple):
        return tuple(map(_convert, node.elts))
    if isinstance(node, _ast.List):
        return list(map(_convert, node.elts))
    if isinstance(node, _ast.Dict):
        return dict([(_convert(k), _convert(v))
                     for (k, v) in zip(node.keys, node.values)])
    #if hasattr(node, 'value') and str(node.value) in _consts:
    #    return node.value         # Python 3.4+
    #if isinstance(node, _ast.Name) and node.id in _consts:
    #    return _consts[node.id]   # Python <= 3.3
    raise ValueError('malformed or disallowed expression')

def literal_eval(expression, _octal_digits=frozenset('01234567')):
    node = compile(expression, '<unknown>', 'eval', _ast.PyCF_ONLY_AST)
    if expression[:1] == '0' and expression[1:2] in _octal_digits:
        raise SyntaxError('unsupported octal notation')
    return _convert(node.body)

def issearchdomain(arg):
    """Check if the argument is a search domain.
    Examples:
      - ``[('name', '=', 'mushroom'), ('state', '!=', 'draft')]``
      - ``['name = mushroom', 'state != draft']``
      - ``[]``
    """
    return isinstance(arg, list) and not (arg and (
        # Not a list of ids: [1, 2, 3]
        isinstance(arg[0], int_types) or
        # Not a list of ids as str: ['1', '2', '3']
        (isinstance(arg[0], basestring) and arg[0].isdigit())))

def searchargs(params, kwargs=None, context=None):
    """Compute the 'search' parameters."""
    if not params:
        return ([],)
    domain = params[0]
    if not isinstance(domain, list):
        return params
    for (idx, term) in enumerate(domain):
        if isinstance(term, basestring) and term not in DOMAIN_OPERATORS:
            m = _term_re.match(term.strip())
            if not m:
                raise ValueError('Cannot parse term %r' % term)
            (field, operator, value) = m.groups()
            try:
                value = literal_eval(value)
            except Exception:
                # Interpret the value as a string
                pass
            domain[idx] = (field, operator, value)
    if (kwargs or context) and len(params) == 1:
        params = (domain,
                  kwargs.pop('offset', 0),
                  kwargs.pop('limit', None),
                  kwargs.pop('order', None),
                  context)
    else:
        params = (domain,) + params[1:]
    return params

if __name__ == "__main__":
    def test(s, kw=None, ctx=None):
        t = s[:]
        print "input: %s,  is?: %s,  parsed: %s" % \
            (t, issearchdomain(s), searchargs((s,), kw, ctx))

    test([('name = Agrolait')])
    test(['name = Agrolait'])
    test('name = Agrolait')
    test(['name = Agrolait'], {'limit': 10}, {'lang': 'js'})
    test(['name = Agrolait', 'type = big'], {'offset': 42}, {'lang': 'js'})
    test(['name = Agrolait', ('type', '=', 'mixed')])

