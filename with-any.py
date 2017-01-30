import logging
import aiohttp.web
from extimulate import endpoint


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    aiohttp.web.run_app(endpoint.app, port=8080)
