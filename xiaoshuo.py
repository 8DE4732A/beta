import aiohttp
from bs4 import BeautifulSoup
from sanic import Sanic
from sanic.response import html, raw

SERVER_NAME = 'http://xs.r.biz'

app = Sanic("xs")

@app.listener('before_server_start')
def init(app, loop):
    pass
    app.ctx.aiohttp_session = aiohttp.ClientSession(loop=loop)

@app.listener('after_server_stop')
def finish(app, loop):
    pass
    loop.run_until_complete(app.ctx.aiohttp_session.close())
    loop.close()

@app.get("/")
async def index(request):
    async with app.ctx.aiohttp_session.get('https://www.74wx.com/60_60910/') as response:
        print("Status:", response.status)
        print("Content-type:", response.headers['content-type'])
        r = await response.text()
        soup = BeautifulSoup(r, 'html.parser')
        dl = soup.select_one('dl')
        for a in dl.select('a'):
            a['href'] = a['href'].replace('/60_60910', '')
        return html(f'<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="utf-8"><title>唐人的餐桌</title></head><body>{dl}</body></html>')

@app.get("/<a>")
async def index(request, a):
    async with app.ctx.aiohttp_session.get('https://www.74wx.com/60_60910/' + a) as response:
        print("Status:", response.status)
        print("Content-type:", response.headers['content-type'])
        r = await response.text()
        soup = BeautifulSoup(r, 'html.parser')
        artical = soup.select_one('#content')
        title = soup.select_one('h1').string
        return html(f'<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="utf-8"><title>{title}</title></head><body>{artical}</body></html>')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10002, access_log=False)
