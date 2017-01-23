import json
import pytest
import asyncio
from unittest import mock
from .. import endpoint
from asyncio_extras.contextmanager import async_contextmanager


def MockSession(data):
    @async_contextmanager
    async def Session():
        @async_contextmanager
        async def get(url):
            async def json():
                return data
            Session.last_url = url
            yield mock.Mock(json=json)
        yield mock.Mock(get=get)
    return Session


@pytest.mark.asyncio
async def test_not_valid():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(users=[]))):
        assert not await endpoint.is_valid("foobar")


@pytest.mark.asyncio
async def test_is_valid():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(users=[dict(username="foobar")]))):
        assert await endpoint.is_valid("foobar")


@pytest.mark.asyncio
async def test_purchases():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(purchases=[dict(productId=1),
                                                                         dict(productId=2)]))):
        assert (await endpoint.purchases("Kiarra86")) == {1, 2}


@pytest.mark.asyncio
async def test_purchases_bad_user():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(purchases=[]))):
        assert not await endpoint.purchases("bad")


@pytest.mark.asyncio
async def test_purchases_escapes_user():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(purchases=[]))) as session:
        assert not await endpoint.purchases("../../foobar")
        # sanity check
        assert session.last_url
        assert "foobar" in session.last_url
        # path traversal attack must be prevented
        assert "../" not in session.last_url


@pytest.mark.asyncio
async def test_who_purchased_empty():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(purchases=[]))):
        assert not await endpoint.who_purchased(123)


@pytest.mark.asyncio
async def test_who_purchased():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(purchases=[dict(username=1),
                                                                         dict(username=2)]))):
        assert (await endpoint.who_purchased(123)) == {1, 2}


@pytest.mark.asyncio
async def test_who_purchased_removes_self():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(purchases=[dict(username=1),
                                                                         dict(username=2),
                                                                         dict(username=42)]))):
        assert (await endpoint.who_purchased(123, skip=42)) == {1, 2}


def ready_future(value):
    f = asyncio.Future()
    f.set_result(value)
    return f


@pytest.mark.asyncio
async def test_recent_purchases_invalid_user():
    with mock.patch("extimulate.endpoint.is_valid", return_value=ready_future(False)), \
            mock.patch("extimulate.endpoint.purchases", return_value=ready_future(None)):
        r = await endpoint.recent_purchases(mock.MagicMock())
        assert r.status == 404


@pytest.mark.asyncio
async def test_recent_purchases_empty():
    with mock.patch("extimulate.endpoint.is_valid", return_value=ready_future(True)), \
            mock.patch("extimulate.endpoint.purchases", return_value=ready_future(set())):
        r = await endpoint.recent_purchases(mock.MagicMock())
        assert r.status == 200
        assert not json.loads(r.text)


@pytest.mark.asyncio
async def test_recent_purchases():
    with mock.patch("extimulate.endpoint.is_valid", return_value=ready_future(True)), \
            mock.patch("extimulate.endpoint.purchases", return_value=ready_future({1})), \
            mock.patch("extimulate.endpoint.product_info", return_value=ready_future(dict(foo="bar"))), \
            mock.patch("extimulate.endpoint.who_purchased", return_value=ready_future({3, 4})):
        r = await endpoint.recent_purchases(mock.MagicMock())
        assert r.status == 200
        assert json.loads(r.text) == [dict(foo="bar", recent=[3, 4])]
