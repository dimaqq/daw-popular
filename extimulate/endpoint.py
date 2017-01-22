import aiohttp.web

async def recent_purchases(request):
    name = request.match_info["username"]
    return aiohttp.web.Response(text="ssss")

app = aiohttp.web.Application()
app.router.add_route("GET", "/api/recent_purchases/{username}", recent_purchases)
