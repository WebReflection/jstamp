# jstamp

Python-to-JavaScript signatures for ESM via introspection.

**[Live Test](https://agiammarchi.pyscriptapps.com/python-to-js-signature/latest/)**

This module's goal is to allow *Python* modules or functions to be exported for *JS* purposes, converting *Python* signatures into the most natural, simplified *JS* counterpart.

#### Background

In *Python* functions, parameters/arguments have a broader meaning than in *JS*.

For example, in *JS*, function `arguments` are always linear (left to right), with a possible default value for each argument.

In *Python*, on the other hand, arguments can be linear (left to right) or named, where named arguments can supersede the linear logic. For example:

```python
def fn(a, **kwargs): pass

fn(True, **{"a": False})
# throws an exception:
# `a` is ambiguous, both passed and as `**kwargs`
```

Lesser known signatures are also possible, something like:

```python
def fn(a, b, /, **kwargs): pass
```

expects positional-only arguments such as `a` and `b` but allows additional arguments afterward as a dictionary.

This module's goal is to convert as meaningfully as possible *Python* expectations into *JS* signatures that meet those expectations through your *IDE* of choice or runtime debugging.

## Signatures

The following signatures are currently compatible with this module:

```python
# generic_module.py
def fn1(a, b, /): pass
def fn2(a, b, /, *args): pass
def fn3(a, b, /, **kwargs): pass
def fn4(*, a, b): pass
def fn5(a, b): pass
def fn6(a, b, **kwargs): pass
def fn7(a, b, *args): pass
def fn8(): pass
def fn9(*args): pass
def fn10(**kwargs): pass
def fn11(*args, **kwargs): pass
```

If your utility, method, or function uses a more convoluted signature, please contact me or file an issue so we can explore how to translate it.

Currently, this module translates those signatures as follows:

```js
// Python:
//   from jstamp import export
//   import generic_module
//   print(export(generic_module))
// Output:

export function fn1(a, b) /* 🐍:fn1(a, b, /) */ {
  const kwargs = {}, args = [a, b];
  return $invoke("fn1", args, kwargs);
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

export function fn10(kwargs) /* 🐍:fn10(**kwargs) */ {
  const args = [];
  return $invoke("fn10", args, kwargs);
}

export function fn11(...args) /* 🐍:fn11(*args, **kwargs) */ {
  const kwargs = args.length && $is_object(args[args.length - 1]) ? args.pop() : {};
  return $invoke("fn11", args, kwargs);
}
```

Each *Python* signature results in a different *JS* one, each providing the expected `args` and `kwargs` to pass along when the *Python* code executes the function.

### Signatures Assumptions

  * `fn(a, b, /)` – With positional-only arguments, there is no attempt to create `kwargs`.
  * `fn(a, b, /, *args)` – Mostly equivalent to `fn(a, b, /)`; no `kwargs`.
  * `fn(a, b, /, **kwargs)` – Enforces `args = [a, b]`; if a third parameter is passed, it is expected to be an object literal for `kwargs`.
  * `fn(*, a, b)` – Accepts only a single object literal argument, so `args` is empty and the argument is always used as `kwargs`.
  * `fn(a, b)` – The most relaxed signature; it is always converted as `{"a": a, "b": b}`. If the function is invoked with a single object literal containing `a` or `b`, that object is passed as `kwargs`.
  * `fn(a, b, **kwargs)` – Works like `fn(a, b)`, but if an extra object is passed, it is merged with the one that produced `a` and `b`. Both `fn(1, 2, { "c": 3 })` and `fn({ "a": 1, "b": 2 }, { "c": 3 })` are valid.
  * `fn(a, b, *args)` – Works similarly to `fn(a, b)` except the remaining arguments are treated as `args` unless a single object is passed as `kwargs`. Both `fn({ "a": 1, "b": 2, "c": 3 })` and `fn(1, 2, 3)` are accepted: the former uses empty `args` and a `kwargs` object; the latter passes `args = [1, 2, 3]` with empty `kwargs`.
  * `fn()` – Whatever you pass, the result is always empty `args` and empty `kwargs`, because the *Python* signature does not accept anything else.
  * `fn(*args)` – Passes a list of `args` with empty `kwargs`.
  * `fn(**kwargs)` – Accepts a single object literal to pass as `kwargs`.
  * `fn(*args, **kwargs)` – Passes a list of `args`; if the last element is an object literal, it is passed as `kwargs` instead of being included in `args`.


## Use Cases

This module allows exporting from the *Python* world any module that exposes functionality invokable from *JS*—whether from a **web page** or **server-side**.

The contract is simple: the *Python* module exports utilities that the generated *JS* module can use and consume (e.g. via asynchronous *API* calls), as long as the `args` and `kwargs` to propagate are clear and the return value can be understood.

## Hooks

To hook into this module's features, pass it a *Python* module and an `invoke` extra argument that dictates what each function should return or how its result should be processed.

By default, that function is:

```js
async function $invoke(name, args, kwargs) {
  const response = await fetch('/jstamp', {
    method: 'POST',
    body: JSON.stringify([name, args, kwargs]),
  });
  // expects a response like [ok, err]
  const [result, error] = await response.json();
  if (error) throw new Error(error);
  return result;
}
```

but you can pass any other `invoke` *JS* function you like to handle the exchange between JS and Python.

**Note:** It is also possible to pass a function without a name:

```js
async function(name, args, kwargs) {
  // ... your logic here
}
```

In this case, the generated code will prefix `const $invoke = ...` automatically.
