from jstamp import transform

import inspect, json

js_utils = """
const { assign: $assign, fromEntries: $fromEntries, prototype: { toString: $toString } } = Object;
const { map: $map, slice: $slice } = Array.prototype;

function $as_kwargs(list, keys) {
  const values = $slice.call(list, 0, keys.length);
  return $fromEntries($map.call(values, $pairs, keys));
}

function $merge_kwargs(list, keys) {
  const { length } = keys;
  const kwargs = $as_kwargs(list, keys);
  return list.length > length ? $assign(kwargs, list[length]) : kwargs;
}

function $is_kwargs(object, keys) {
  return $is_object(object) && keys.some($owned, object);
}

function $is_object(object) {
  return $toString.call(object) === "[object Object]";
}

function $owned(key) {
  return this.hasOwnProperty(key);
}

function $pairs(value, index) {
  return [this[index], value];
}

function $invoke(name, args, kwargs) {
  // TBD - result into Python name(*args, **kwargs)
  return { name, args, kwargs };
}
"""

from pyscript import document

area = document.getElementById('code')
output = document.getElementById('output')

def oninput(e):
    try:
        code = area.value.strip()
        output.textContent = code
        locals = {}
        exec(code, {}, locals)
        output.textContent = ''
        for name, value in locals.items():
            if callable(value):
                output.textContent += transform(value) + '\n\n'
        output.textContent += '// JS: utilities to resolve args' + js_utils
        output.className = ''

    except Exception as e:
        output.className = 'error'
        output.textContent = str(e)

area.oninput = oninput

oninput({})

