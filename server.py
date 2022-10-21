import aiohttp
from bs4 import BeautifulSoup
from sanic import Sanic
from sanic.response import html, raw

SERVER_NAME = 'http://localhost'

app = Sanic("cnbeta")

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
async def cnbeta(request):
    async with app.ctx.aiohttp_session.get('https://www.cnbeta.com/') as response:
        print("Status:", response.status)
        print("Content-type:", response.headers['content-type'])
        r = await response.text()
        soup = BeautifulSoup(r, 'html.parser')
        items = []
        for item in soup.select('.item'):
            a = item.select_one('dl > dt > a')
            if a is not None and a.has_attr('href'):
                a['href'] = a['href'].replace('https://www.cnbeta.com', SERVER_NAME).replace('//hot.cnbeta.com', SERVER_NAME + '/hot')
                del a['target']
                items.append(str(a))
        articals = '<br/>'.join(items)
        return html(f'<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="utf-8"><title>cnbeta</title></head><body>{articals}</body></html>')

@app.get("/hot/<a>/<b>")
@app.get("/articles/<a>/<b>")
async def articles(request, a, b):
    url = None
    print(request.path)
    if request.path.startswith('/articles'):
        url = 'https://www.cnbeta.com'
    elif request.path.startswith('/hot'):
        url = 'https://hot.cnbeta.com'

    async with app.ctx.aiohttp_session.get(url + request.path) as response:
        print("Status:", response.status)
        print("Content-type:", response.headers['content-type'])
        r = await response.text()
        soup = BeautifulSoup(r, 'html.parser')
        for img in soup.select('img'):
            if img.has_attr('src'):
                img['src'] = img['src'].replace('https://static.cnbetacdn.com', SERVER_NAME + '/cdn')
        article_summary = soup.select_one('.article-summary')
        article_content = soup.select_one('.article-content')
        title = soup.select_one('title').string
        return html('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="utf-8"><style>img {max-width:90%;}</style>' + f'<title>{title}</title></head><body>{article_summary}{article_content}</body></html>')

@app.get("/cdn/<a>/<b>")
@app.get("/cdn/<a>/<b>/<c>/<d>")
@app.get("/cdn/<a>/<b>/<c>/<d>/<e>")
async def cdn(request, a, b, c = '', d = '', e = ''):
    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.cnbeta.com/',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    async with app.ctx.aiohttp_session.get(f'https://static.cnbetacdn.com' + request.path[4:] , headers=headers) as response:
        print("Status:", response.status)
        print("Content-type:", response.headers['content-type'])
        r = await response.read()
        return raw(r, content_type=response.headers['content-type'])
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, access_log=False)