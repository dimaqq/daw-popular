import logging
from asyncio import ensure_future
import aiohttp.web
import os

HOST = os.environ.get("UPSTREAM_HOST", "74.50.59.155:6000")


async def is_valid(username):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{HOST}/api/users") as r:
            users = {u["username"] for u in (await r.json())["users"]}
            return username in users


async def purchases(username):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{HOST}/api/purchases/by_user/{username}?limit=5") as r:
            return (await r.json())["purchases"]


async def recent_purchases(request):
    name = request.match_info["username"]
    valid = ensure_future(is_valid(name))
    ps = ensure_future(purchases(name))
    if not await valid:
        raise Exception("ouch")
    rv = "sss"
    return aiohttp.web.Response(text=rv,
                                headers={"ETag": str(hash(rv)),
                                         "Cache-Control": "600"})  # public, let varnish cache it

app = aiohttp.web.Application()
app.router.add_route("GET", "/api/recent_purchases/{username}", recent_purchases)
