import os
import json
import logging
from urllib.request import quote
from asyncio import ensure_future
import aiohttp.web

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


async def who_purchased(prod_id, skip=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{HOST}/api/purchases/by_product/{prod_id}") as r:
            return {p["username"] for p in (await r.json())["purchases"] if p["username"] != skip}


async def product_info(prod_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{HOST}/api/products/{prod_id}") as r:
            logging.debug("info: %s", await r.json())
            return (await r.json())["product"]


async def recent_purchases(request):
    name = request.match_info["username"]
    valid = ensure_future(is_valid(name))
    ps = ensure_future(purchases(name))

    if not await valid:
        return aiohttp.web.Response(status=404,
                                    text=f"User with username of {name!r} was not found",
                                    headers={"Cache-Control": "max-age=600, public"})

    logging.debug("user %r if valid", name)

    infos = {pid: ensure_future(product_info(pid)) for pid in await ps}
    whos = {pid: ensure_future(who_purchased(pid, skip=name)) for pid in await ps}

    rv = sorted([{**(await v), "recent": list(await whos[k])} for k, v in infos.items()],
                key=lambda el: -len(el["recent"]))
    
    rv = json.dumps(rv)
    return aiohttp.web.Response(text=rv,
                                headers={"ETag": str(hash(rv)),
                                         "Cache-Control": "max-age=600, public"})  # let varnish and broser cache it

app = aiohttp.web.Application()
app.router.add_route("GET", "/api/recent_purchases/{username}", recent_purchases)
