from inspect import getmembers, signature
from json import dumps
from sys import version

IS_MICROPYTHON = 'MicroPython' in version

__all__ = ['export', 'transform']

_code = """
const { assign, fromEntries, prototype: { toString } } = Object;
const { map, slice } = Array.prototype;

function as_kwargs(list, keys) {
  const values = slice.call(list, 0, keys.length);
  return fromEntries(map.call(values, (v, i) => [keys[i], v]));
}

function merge_kwargs(list, keys) {
  const { length } = keys;
  const kwargs = as_kwargs(list, keys);
  return list.length > length ? assign(kwargs, list[length]) : kwargs;
}

function is_kwargs(object, keys) {
  return is_object(object) && keys.some(owned, object);
}

function is_object(object) {
  return toString.call(object) === "[object Object]";
}

function owned(key) {
  return this.hasOwnProperty(key);
}
"""

_invoke = """
async function invoke(name, args, kwargs) {
  const response = await fetch('/python_js', {
    method: 'POST',
    body: JSON.stringify({ name, args, kwargs }),
  });
  return response.json();
}
"""

def _signature(name, sig):
    signature = str(sig)
    return ' ' if signature.startswith('<') else f' /* 🐍:{name}{signature} */ '

def transform(fn):
    sig = signature(fn)
    keys = []
    has_args = False
    has_kwargs = False
    has_positional_only = False
    has_keyword_only = False
    i = 0

    for param in sig.parameters.values():
        # MicroPython only
        if IS_MICROPYTHON:
            keys.append(param)
        # MicroPython + CPython
        elif param.kind == param.KEYWORD_ONLY:
            has_keyword_only = True
        elif param.kind == param.POSITIONAL_OR_KEYWORD or has_keyword_only:
            keys.append(param.name)
            if param.kind == param.KEYWORD_ONLY:
                has_keyword_only = True
        elif param.kind == param.POSITIONAL_ONLY:
            has_positional_only = True
            keys.append(param.name)
            i += 1
        elif param.kind == param.VAR_POSITIONAL:
            has_args = True
        elif param.kind == param.VAR_KEYWORD:
            has_kwargs = True

    js = f'export{_signature(fn.__name__, sig)}function {fn.__name__}('

    # keys make no sense so far in MicroPython
    # everything is handled as just args 🤷
    if IS_MICROPYTHON:
        js += '...args) {'
        js += '\n  const kwargs = {};'
        pass

    # CPython only
    elif keys:
        # test(a, b, /)
        if has_positional_only:
            js += ', '.join(keys)
            # test(a, b, /, *args)
            # test(a, b, /, **kwargs)
            js += ', ...$) {' if has_args else ', $ = {}) {' if has_kwargs else ') {'
            js += '\n  const kwargs = '
            js += '$' if has_kwargs else '{}'
            js += ', args = '
            js += f'[{', '.join(keys)}, ...$];' if has_args else  f'[{', '.join(keys)}];'

        # # test(*, a, b)
        # TODO: this is a weird case I need to either ignore for reasons or handle
        # elif has_keyword_only: pass

        # fn(a, b)
        # fn(a, b, **kwargs)
        elif not has_args:
            json_keys = dumps(keys)
            js += ', '.join(keys) + ') {'
            js += f'\n  const args = [], kwargs = arguments.length === 1 && is_kwargs({keys[0]}, {json_keys}) ? {keys[0]} : {'merge_kwargs' if has_kwargs else 'as_kwargs'}(arguments, {json_keys});'

        # fn(a, b, *args)
        elif has_args and not has_kwargs:
            js += ', '.join(keys) + ', ...$) {'
            js += '\n  let args = [], kwargs;'
            js += f'\n  if (arguments.length === 1 && is_kwargs({keys[0]}, {dumps(keys)})'
            js += f'\n    kwargs = {keys[0]};'
            js += '\n  else {'
            js += '\n    kwargs = {};'
            js += f'\n    args.push({', '.join(keys)}, ...$);'
            js += '\n  }'

    # test(*, a, b)
    elif has_keyword_only:
        js += 'kwargs = {}) {'
        js += '\n  const args = [];'

    # fn()
    elif not (has_args or has_kwargs):
        js += ') {'
        js += '\n  const args = [], kwargs = {};'

    # fn(*args)
    elif has_args and not has_kwargs:
        js += '...args) {'
        js += '\n  const kwargs = {};'

    # fn(**kwargs)
    elif has_kwargs and not has_args:
        js += 'kwargs) {'
        js += '\n  const args = [];'

    # fn(*args, **kwargs)
    else:
        js += '...$) {'
        js += '\n  const { length } = $;'
        js += '\n  let args = $, kwargs;'
        js += '\n  if (length < 1) kwargs = {};'
        js += '\n  else if (is_object($[length - 1])) kwargs = $.pop();'

    js += '\n  return invoke(' + dumps(fn.__name__) + ', args, kwargs);'
    js += '\n}'

    return js

def export(module, invoke=_invoke):
    exports = [invoke.strip()]
    for name, value in getmembers(module):
        if not name.startswith('_') and callable(value):
            exports.append(transform(value))
    exports.append(_code.strip())
    return '\n\n'.join(exports)
