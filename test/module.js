const $invoke = function (name, args, kwargs) {
  return { name, args, kwargs };
};

export function fn1(a, b) /* 🐍:fn1(a, b, /) */ {
  const kwargs = {}, args = [a, b];
  return $invoke("fn1", args, kwargs);
}

export function fn10(kwargs) /* 🐍:fn10(**kwargs) */ {
  const args = [];
  return $invoke("fn10", args, kwargs);
}

export function fn11(...args) /* 🐍:fn11(*args, **kwargs) */ {
  const kwargs = args.length && $is_object(args[args.length - 1]) ? args.pop() : {};
  return $invoke("fn11", args, kwargs);
}

export function fn2(a, b, ...$) /* 🐍:fn2(a, b, /, *args) */ {
  const kwargs = {}, args = [a, b, ...$];
  return $invoke("fn2", args, kwargs);
}

export function fn3(a, b, $ = {}) /* 🐍:fn3(a, b, /, **kwargs) */ {
  const kwargs = $, args = [a, b];
  return $invoke("fn3", args, kwargs);
}

export function fn4(kwargs = {}) /* 🐍:fn4(*, a, b) */ {
  const args = [];
  return $invoke("fn4", args, kwargs);
}

export function fn5(a, b) /* 🐍:fn5(a, b) */ {
  const args = [], kwargs = arguments.length === 1 && $is_kwargs(a, ["a", "b"]) ? a : $as_kwargs(arguments, ["a", "b"]);
  return $invoke("fn5", args, kwargs);
}

export function fn6(a, b) /* 🐍:fn6(a, b, **kwargs) */ {
  const args = [], kwargs = arguments.length === 1 && $is_kwargs(a, ["a", "b"]) ? a : $merge_kwargs(arguments, ["a", "b"]);
  return $invoke("fn6", args, kwargs);
}

export function fn7(a, b, ...$) /* 🐍:fn7(a, b, *args) */ {
  let args = [], kwargs;
  if (arguments.length === 1 && $is_kwargs(a, ["a", "b"]))
    kwargs = a;
  else {
    kwargs = {};
    args.push(a, b, ...$);
  }
  return $invoke("fn7", args, kwargs);
}

export function fn8() /* 🐍:fn8() */ {
  const args = [], kwargs = {};
  return $invoke("fn8", args, kwargs);
}

export function fn9(...args) /* 🐍:fn9(*args) */ {
  const kwargs = {};
  return $invoke("fn9", args, kwargs);
}

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
