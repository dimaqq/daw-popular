import logging
import aiohttp.web
from . import endpoint


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    aiohttp.web.run_app(endpoint.app, port=8080)

