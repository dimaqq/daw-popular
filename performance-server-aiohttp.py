import asyncio
import aiohttp.web


async def recent_purchases(request):
    await asyncio.sleep(0.01)

    return aiohttp.web.Response(text="done")

app = aiohttp.web.Application()
app.router.add_route("GET", "/api/recent_purchases/{username}", recent_purchases)
aiohttp.web.run_app(app, port=8080)
