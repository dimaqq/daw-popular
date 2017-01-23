import pytest
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
