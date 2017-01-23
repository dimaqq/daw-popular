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
