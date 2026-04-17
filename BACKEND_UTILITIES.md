# Backend Utilities Reference Guide

This document provides a quick reference for the new backend utility modules added in v1.1.1.

## Module Overview

### 1. sanitizers.py
**Purpose**: Input sanitization and validation

**Key Classes**:
- `Sanitizer` - String, mobile, seat, and CSV field sanitization
- `InputValidator` - Advanced validation for seat lists, mobile numbers, dates

**Usage**:
```python
from app.sanitizers import InputValidator

# Validate seats
validated_seats = InputValidator.validate_seat_list(["A1", "A2"])

# Validate mobile
mobile = InputValidator.validate_mobile_number("9876543210")

# Validate date
date_str = InputValidator.validate_travel_date("2024-12-25")
```

### 2. performance.py
**Purpose**: Performance monitoring and profiling

**Key Classes**:
- `PerformanceMonitor` - Measure function execution time
- `DatabasePerformance` - Database query performance tracking
- `CachePerformance` - Cache hit/miss statistics

**Usage**:
```python
from app.performance import PerformanceMonitor, get_cache_statistics

# Decorator usage
@PerformanceMonitor.measure_time("get_bookings")
def get_bookings():
    pass

# Context manager usage
with PerformanceMonitor.timer("database_query"):
    # Your code here
    pass

# Get cache stats
stats = get_cache_statistics()
```

### 3. db_optimization.py
**Purpose**: Database optimization and query helpers

**Key Classes**:
- `QueryOptimizer` - Query execution plan analysis
- `IndexManager` - Recommended indexes and scripts
- `DatabaseTuning` - Database configuration recommendations

**Usage**:
```python
from app.db_optimization import IndexManager

# Get index creation script
sqlite_script = IndexManager.create_index_script("sqlite")
postgresql_script = IndexManager.create_index_script("postgresql")

# Get recommendations
recommended = IndexManager.get_recommended_indexes()
```

### 4. rate_limiting.py
**Purpose**: Rate limiting and throttling configuration

**Key Classes**:
- `RateLimitConfig` - Configure rate limits by tier
- `EndpointRateLimits` - Per-endpoint rate limits
- `ThrottleStrategies` - Fixed window and token bucket strategies

**Usage**:
```python
from app.rate_limiting import EndpointRateLimits, ThrottleStrategies

# Get endpoint limit
limit, burst = EndpointRateLimits.get_limit("/api/bookings")

# Token bucket strategy
allowed, info = ThrottleStrategies.token_bucket(
    tokens=10,
    capacity=100,
    refill_rate=2.0,
    last_refill=time.time()
)
```

### 5. caching.py
**Purpose**: Caching strategies and management

**Key Classes**:
- `InMemoryCache` - In-memory cache with TTL support
- `CacheManager` - Centralized cache management
- `CachePatterns` - Cache-aside, write-through, write-behind patterns

**Usage**:
```python
from app.caching import cached, cache_manager, CachePatterns

# Decorator usage
@cached(ttl=300, namespace="bookings")
def get_bookings(travel_date):
    # Function code
    pass

# Direct cache usage
cache = cache_manager.get_cache("bookings")
cache.set("key", value, ttl=300)
value = cache.get("key")

# Cache patterns
value = CachePatterns.cache_aside(
    key="seat_map_2024-12-25",
    load_func=lambda: fetch_from_db(),
    ttl=300
)
```

## Integration Examples

### Complete Example: Optimized Booking Retrieval

```python
from app.sanitizers import InputValidator
from app.caching import CachePatterns, CACHE_TTLS
from app.performance import PerformanceMonitor

@PerformanceMonitor.measure_time("get_bookings_optimized")
def get_bookings_optimized(travel_date: str):
    # Validate input
    validated_date = InputValidator.validate_travel_date(travel_date)
    
    # Try cache
    cache_key = f"bookings:{validated_date}"
    bookings = CachePatterns.cache_aside(
        key=cache_key,
        load_func=lambda: fetch_bookings_from_db(validated_date),
        ttl=CACHE_TTLS["booking_list"]
    )
    
    return bookings
```

### Database Optimization Setup

```python
from app.db_optimization import IndexManager

# Generate index script
script = IndexManager.create_index_script("sqlite")

# Execute indexes
with db_connection:
    db_connection.executescript(script)
```

## Best Practices

1. **Input Sanitization**
   - Always sanitize user input before database queries
   - Validate format and length constraints

2. **Performance Monitoring**
   - Use decorators for automatic time tracking
   - Monitor slow operations (>100ms)
   - Review cache hit ratios regularly

3. **Database Optimization**
   - Create recommended indexes
   - Use pagination for large queries
   - Analyze query plans for slow queries

4. **Caching**
   - Use appropriate TTLs based on data freshness requirements
   - Monitor cache hit ratios
   - Invalidate cache on data updates

5. **Rate Limiting**
   - Apply per-endpoint limits
   - Use token bucket for bursty traffic
   - Return clear rate limit headers

## Configuration

### Environment Variables
```env
# Caching
CACHE_TTL_SEAT_MAP=300
CACHE_TTL_BOARDING_SEQUENCE=300

# Performance
SLOW_QUERY_THRESHOLD_MS=100
SLOW_OPERATION_THRESHOLD_MS=1000

# Rate Limiting
DEFAULT_RATE_LIMIT=100
DEFAULT_BURST_SIZE=5
```

## Monitoring & Metrics

### Cache Statistics
```python
stats = get_cache_statistics()
# Output: {"hits": 150, "misses": 50, "total": 200, "hit_ratio_percent": 75.0}
```

### Performance Logs
```
[DEBUG] get_bookings completed: duration_ms=45.32
[WARNING] database_query took 1250ms (slow)
```

## Future Enhancements

- [ ] Redis integration for distributed caching
- [ ] Advanced rate limiting with per-user limits
- [ ] Query result caching with smart invalidation
- [ ] Database connection pooling optimization
- [ ] Distributed cache synchronization
