# Discount Ascii Warehouse Popular Products Service
TBD
### For the eggs team ;-)
TBD

### Design considerations
* made for the web (scale, server-side cache, client-side cache)
* docker (testable, scalable, deployment)
* asyncio (why not? also insane concurrency)
* ...

### Done
* skeleton
* dockerise
* tox and pytest for unit tests

### Plan
* free online test runner
* xxx
* base code (wsgi? asyncio bottle ...)
* routes
* fixed responses
* actual code
* ...
* cache control for browser

### Maybe later
* black box tests (microservice in isolation)
* acceptance tests (uses real data server)
* http2?
* ETag and If-Match validation
* anti-dogpile when making upstream requests
