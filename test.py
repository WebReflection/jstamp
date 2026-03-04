from jstamp import export
import test_module

invoke = """
function invoke(name, args, kwargs) {
  return { name, args, kwargs };
}
"""

print(export(test_module, invoke))
