const { isArray } = Array;
const { ownKeys } = Reflect;
const { stringify } = JSON;

const $invoke = `
function $invoke(name, args) {
  const response = await fetch('/jstamp', {
    method: 'POST',
    body: JSON.stringify([name, args]),
  });
  const [result, error] = await response.json();
  if (error) throw new Error(error);
  return result;
}
`;

export const guard = (module, request) => {
  if (
    !isArray(request) ||
    request.length !== 2 ||
    typeof request[0] !== 'string' ||
    !isArray(request[1]) ||
    !/^[a-z]/.test(request[0]) ||
    typeof module[request[0]] !== 'function'
  ) {
    throw new TypeError('Invalid request');
  }
  return module[request[0]](...request[1]);
};

export default (module, invoke = $invoke) => {
  const exports = [(typeof invoke === 'function' ? `const $invoke = ${invoke};` : String(invoke)).trim()];
  if (!exports[0].includes(' $invoke'))
    exports[0] = `const $invoke = ${exports[0]};`;
  for (const name of ownKeys(module)) {
    if (typeof name === 'string' && /^[a-z]/.test(name) && typeof module[name] === 'function') {
      exports.push(`const ${name} = (...args) => $invoke(${stringify(name)}, args);`);
    }
  }
  return exports.join('\n\n') + '\n';
};
