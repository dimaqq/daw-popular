# Discount Ascii Warehouse Popular Products Service
TBD
### For the eggs team ;-)
TBD

### Quick start
run `docker-compose -f docker-compose.yml up --build`
test `http localhost/api/recent_purchases/Kiarra86`

### Uni tests
run `tox` (Python3.6 must be available)

### Branches
* master (https://github.com/dimaqq/daw-popular/tree/master) demo code
* performance (https://github.com/dimaqq/daw-popular/tree/performance) fast asyncio (uvloop, httptools)
* curio-h11 (https://github.com/dimaqq/daw-popular/tree/curio-h11) compromise between performance and API
* pure-python (TBD) caching in Python, that is without HTTP cache

### Design considerations
* made for the web (scale, server-side cache, client-side cache)
* docker (testable, scalable, deployment)
* asyncio (why not? also insane concurrency)
* anti-dogpile (of some sort)

### Architecture

![option1](https://github.com/dimaqq/daw-popular/raw/master/doc/arch-option1.png "Option 1")

![option2](https://github.com/dimaqq/daw-popular/raw/master/doc/arch-option2.png "Option 2")

### Done
* skeleton
* dockerise
* tox and pytest for unit tests
* free online test pipeline
* code coverage (hidden under circle ci artefacts)
* sync bottle skeleton
* asyncio server skeleton, front-end cache works
* route
* fixed responses
* cache control for browser
* ETag
* bug: protect against bad username
* actual code
* manual testing

### Plan
* figure out how to mock asyncio dependencies
* bug: varnish containers should exit faster

### Maybe later
* black box tests (microservice in isolation)
* acceptance tests (uses real data server)
* http2?
* pure-python: anti-dogpile when making upstream requests

### Tools
* https://circleci.com/gh/dimaqq/daw-popular
* https://coveralls.io/github/dimaqq/daw-popular
* https://codeclimate.com/github/dimaqq/daw-popular
