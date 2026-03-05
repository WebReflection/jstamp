from jstamp import export
import test_module

invoke = """
function (name, args, kwargs) {
  return { name, args, kwargs };
}
"""

with open('./test/module.js', 'w') as f:
    f.write(export(test_module, invoke))
