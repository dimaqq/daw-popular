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
            r = mock.Mock()
            r.json = json
            yield r

        rv = mock.Mock()
        rv.get = get
        yield rv
    return Session


@pytest.mark.asyncio
async def test_not_valid():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(users=[]))):
        assert not await endpoint.is_valid("foobar")


@pytest.mark.asyncio
async def test_is_valid():
    with mock.patch("aiohttp.ClientSession", MockSession(dict(users=[dict(username="foobar")]))):
        assert await endpoint.is_valid("foobar")


@pytest.mark.skip(reason="can't find working asyncio mock")
@pytest.mark.asyncio
@mock.patch("aiohttp.ClientSession")
async def test_purchases(session):
    assert (await endpoint.purchases("Kiarra86")) == {1, 2}


@pytest.mark.skip(reason="can't find working asyncio mock")
@pytest.mark.asyncio
@mock.patch("aiohttp.ClientSession")
async def test_purchases_bad_user(session):
    assert not await endpoint.purchases("bad")


@pytest.mark.skip(reason="can't find working asyncio mock")
@pytest.mark.asyncio
@mock.patch("aiohttp.ClientSession")
async def test_purchases_escapes_user(session):
    assert not await endpoint.purchases("../../foobar")
