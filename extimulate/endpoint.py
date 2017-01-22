import aiohttp.web

async def recent_purchases(request):
    name = request.match_info["username"]
    rv = "sss"
    return aiohttp.web.Response(text=rv,
                                headers={"ETag": str(hash(rv)),
                                         "Cache-Control": "600"})  # public, let varnish cache it

app = aiohttp.web.Application()
app.router.add_route("GET", "/api/recent_purchases/{username}", recent_purchases)
