# Discount Ascii Warehouse Popular Products Service
TBD
### For the eggs team ;-)
TBD

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

### Plan
* actual code
* ...
* cache control for browser

### Maybe later
* black box tests (microservice in isolation)
* acceptance tests (uses real data server)
* http2?
* ETag and If-Match validation
* cache upstream resuls via nginx?
* cache responses via nginx?
* anti-dogpile when making upstream requests

### Tools
* https://circleci.com/gh/dimaqq/daw-popular
* https://coveralls.io/github/dimaqq/daw-popular
* https://codeclimate.com/github/dimaqq/daw-popular
