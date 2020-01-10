# Find Replacement policy

## Broadwell
### LRU

**Scenario**: J1, J2, J3, J4, J5, J1, J2, J3, J4, J5

Expectation: Once the set is full (4 jumps), we see one eviction for each following jump as they repeat in the same order but have been evicted before so 1 resteer each time.

**Observations**: 2 evictions -> **Not LRU**

### FIFO

Same scenario proves that is **not FIFO** either.

### LIFO

Same scenario shows that it is **not LIFO** because we expect 3 resteers: on the first J5, the second J4 and the second J5.

### What is it then?

**Scenario 1**: J1, J2, J3, J4, J5, J5

Repeat J5 another time to see if we resteer. We do: 2 evictions

**Scenario 2**: J1, J2, J3, J4, J5, J5, J5 (and more J5)

We remain at 2 resteers, no matter the amount of J5 repeatings -> it is in the BTB. There seems to be a system such that we do not evict "hot branches". Maybe a single bit to mark an entry for eviction and on the second time it gets evicted (the first time only marked).

**Scenario 3**: J1, J2, J3, J4, J5, J2, J3, J4, J5, J2, J3, J4, J5

To see which branch gets evicted: if we still have 2 evictions, it is J1 if it is another branch (J2, J3, J4, J5), we expect to see a higher number of resteers as the branches reevict each other.

We still have 2 resteers -> LRU with a strike system to evict on the second strike

## Skylake

### LRU

**Scenario**: J1, J2, J3, J4, J5, J1, J2, J3, J4, J5

Expectation: Once the set is full (4 jumps), we see one eviction for each following jump as they repeat in the same order but have been evicted before so 1 resteer each time.

### 

More details in the report sections 4.1.5 (Broadwell) and 4.2.5 (Skylake). 