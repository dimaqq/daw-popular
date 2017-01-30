import logging
import aiohttp.web
from extimulate import endpoint


if __name__ == "__main__":
    import statprof
    statprof.start()
    try:
        logging.basicConfig(level=logging.INFO)
        aiohttp.web.run_app(endpoint.app, port=8080)
    finally:
        statprof.stop()
        statprof.display()
