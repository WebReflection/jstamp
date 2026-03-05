import asyncio

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

from jstamp import export
import module
import json

app = FastAPI()

# JStamp API
jstamp_path = '/🐍'
jstamp_content = export(module, """
async function $invoke(name, args, kwargs) {
  const response = await fetch('""" + jstamp_path + """', {
    method: 'POST',
    body: JSON.stringify([name, args, kwargs]),
  });
  const [result, error] = await response.json();
  if (error) throw new Error(error);
  return result;
}
""")

@app.middleware("http")
async def jstamp(request, call_next):
    if request.url.path == jstamp_path:
        method = request.method
        if method == 'POST':
            headers = { 'Content-Type': 'application/json' }
            try:
                name, args, kwargs = await request.json()
                method = getattr(module, name)
                content = [method(*args, **kwargs), None]
            except Exception as e:
                content = [None, str(e)]
            content = json.dumps(content)
        else:
            headers = { 'Content-Type': 'text/javascript' }
            content = jstamp_content

        response = Response(status_code=200, headers=headers, content=content)

    else:
        response = await call_next(request)

    return response

app.mount('/', StaticFiles(directory='public', html=True), name='public')
