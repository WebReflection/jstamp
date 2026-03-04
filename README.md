# jstamp

Python to JavaScript signatures for ESM out of introspection.

**[Live Test](https://agiammarchi.pyscriptapps.com/python-to-js-signature/latest/)**

This module goal is to allow *Python* modules or functions to be exported for *JS* purposes, trying to convert *Python* signatures into the most natural, simplified, *JS* counterpart.

#### Background

In *Python* functions, parameters/arguments have a broader meaning than in *JS*.

As example, in *JS* function `arguments` are always linear, left to right, with possible default value per each argument.

On the other hand, in *Python* arguments can be linear (left to right) or named, where named somehow superseeds the linear logic, example:

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

expects positional arguments such as `a` and `b` but it allows other arguments after, as dictionary.

This module goal is to convert as meaningfully as possible *Python* expectations into *JS* signatures that meet those expectations through your *IDE* of choice or runtime debugging.

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

If your utility/method/function is using a way more convoluted signature, please contact me, or file an issue, to understand how that could be translated.

Right now, this module translates those signatures as such:

```js
// Python:
//   from jstamp import export
//   import generic_module
//   print(export(generic_module))
// Output:

export /* 🐍:fn1(a, b, /) */ function fn1(a, b) {
  const kwargs = {}, args = [a, b];
  return invoke("fn1", args, kwargs);
}

export /* 🐍:fn2(a, b, /, *args) */ function fn2(a, b, ...$) {
  const kwargs = {}, args = [a, b, ...$];
  return invoke("fn2", args, kwargs);
}

export /* 🐍:fn3(a, b, /, **kwargs) */ function fn3(a, b, $ = {}) {
  const kwargs = $, args = [a, b];
  return invoke("fn3", args, kwargs);
}

export /* 🐍:fn4(*, a, b) */ function fn4(kwargs = {}) {
  const args = [];
  return invoke("fn4", args, kwargs);
}

export /* 🐍:fn5(a, b) */ function fn5(a, b) {
  const args = [], kwargs = arguments.length === 1 && is_kwargs(a, ["a", "b"]) ? a : as_kwargs(arguments, ["a", "b"]);
  return invoke("fn5", args, kwargs);
}

export /* 🐍:fn6(a, b, **kwargs) */ function fn6(a, b) {
  const args = [], kwargs = arguments.length === 1 && is_kwargs(a, ["a", "b"]) ? a : merge_kwargs(arguments, ["a", "b"]);
  return invoke("fn6", args, kwargs);
}

export /* 🐍:fn7(a, b, *args) */ function fn7(a, b, ...$) {
  let args = [], kwargs;
  if (arguments.length === 1 && is_kwargs(a, ["a", "b"])
    kwargs = a;
  else {
    kwargs = {};
    args.push(a, b, ...$);
  }
  return invoke("fn7", args, kwargs);
}

export /* 🐍:fn8() */ function fn8() {
  const args = [], kwargs = {};
  return invoke("fn8", args, kwargs);
}

export /* 🐍:fn9(*args) */ function fn9(...args) {
  const kwargs = {};
  return invoke("fn9", args, kwargs);
}

export /* 🐍:fn10(**kwargs) */ function fn10(kwargs) {
  const args = [];
  return invoke("fn10", args, kwargs);
}

export /* 🐍:fn11(*args, **kwargs) */ function fn11(...$) {
  const { length } = $;
  let args = $, kwargs;
  if (length < 1) kwargs = {};
  else if (is_object($[length - 1])) kwargs = $.pop();
  return invoke("fn11", args, kwargs);
}
```

Each *Python* signature results into a different *JS* one, all ending up providing the right amount, or expected, `args` and `kwargs` to pass along once the *Python* code needs to execute such function.

## Use Cases

This module allows to export from the *Python* world any module that exposes functionalities able to be invoked through *JS*, either via a **Web page** or any other **Server side** meaning.

The contract is simple: the python module exports utilities the produced *JS* module can use and consume, via asynchronous *API* calls or something else, as long as the `args` and `kwargs` input to propagate is clear and the returned value can be understood.

## Hooks

To hook into this module features all you need is to pass it a *Python* *module* and an `invoke` extra argument that dictates what each function should return or how its result should be processed.

By default, that function is the following one:

```js
async function invoke(name, args, kwargs) {
  const response = await fetch('/python_js', {
    method: 'POST',
    body: JSON.stringify({ name, args, kwargs }),
  });
  return response.json();
}
```

but you can pass along any other `invoke` *JS* function yuo like to see the exchange between JS and Python happening.
