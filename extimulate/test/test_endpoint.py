import pytest
from unittest import mock
from .. import endpoint


@pytest.mark.skip(reason="can't find working asyncio mock")
@pytest.mark.asyncio
async def test_not_valid():
    with mock.patch("aiohttp.ClientSession", AsyncMock()):
        assert not await endpoint.is_valid("foobar")


@pytest.mark.skip(reason="can't find working asyncio mock")
@pytest.mark.asyncio
async def test_is_valid():
    with asynctest.patch("aiohttp.ClientSession"):
        assert await endpoint.is_valid("Kiarra86")


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
