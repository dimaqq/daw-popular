import logging
from urllib.request import quote
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
        async with session.get(f"http://{HOST}/api/purchases/by_user/{quote(username, safe=[])}?limit=5") as r:
            return {p["productId"] for p in (await r.json())["purchases"]}


async def recent_purchases(request):
    name = request.match_info["username"]
    valid = ensure_future(is_valid(name))
    ps = ensure_future(purchases(name))

    if not await valid:
        return aiohttp.web.Response(status=404,
                                    text=f"User with username of {name!r} was not found",
                                    headers={"Cache-Control": "max-age=600, public"})

    logging.debug("user %r if valid", name)
    logging.debug("purchases %r", await ps)

    rv = "sss"
    return aiohttp.web.Response(text=rv,
                                headers={"ETag": str(hash(rv)),
                                         "Cache-Control": "max-age=600, public"})  # let varnish and broser cache it

app = aiohttp.web.Application()
app.router.add_route("GET", "/api/recent_purchases/{username}", recent_purchases)
