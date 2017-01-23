### Concurrency

Setup:
* bypass front-end cache
* hit python business logic
* source data is already cached

```
conc  ms mean
-------------
   1       51
   2      121
   4      215
  10      473
 100     4441
1000   errors
```

Workload is CPU-bound (expected), but 50ms per request is apalling

According to the following, aiohttp is the bottleneck
* https://magic.io/blog/uvloop-blazing-fast-python-networking/
* https://github.com/KeepSafe/aiohttp/issues/858

A new set of libraries is required for adequate performance.
