"""Profile the startup and view-refresh timing."""
import sys, time
sys.path.insert(0, '_internal')

results = {}

# DB import
t0 = time.perf_counter()
import database
results['import database'] = time.perf_counter() - t0

# Connection
t0 = time.perf_counter()
ok, msg = database.test_connection()
results['first connection'] = time.perf_counter() - t0

# Individual queries (cold - no cache)
database.invalidate_cache()
for fn_name in ['get_fields', 'get_crops_with_fields', 'get_inventory']:
    fn = getattr(database, fn_name)
    t0 = time.perf_counter()
    fn()
    results[f'{fn_name} (cold)'] = time.perf_counter() - t0

# Dashboard metrics
database.invalidate_cache()
t0 = time.perf_counter()
database.get_dashboard_metrics()
results['get_dashboard_metrics (cold)'] = time.perf_counter() - t0

# Upcoming activities
database.invalidate_cache()
t0 = time.perf_counter()
database.get_upcoming_activities(30)
results['get_upcoming_activities (cold)'] = time.perf_counter() - t0

# Warm (cached)
for fn_name in ['get_fields', 'get_crops_with_fields', 'get_inventory']:
    fn = getattr(database, fn_name)
    t0 = time.perf_counter()
    fn()
    results[f'{fn_name} (warm/cached)'] = time.perf_counter() - t0

# All dashboard queries combined (simulating _warm_all_views serial)
database.invalidate_cache()
t0 = time.perf_counter()
database.get_dashboard_metrics()
database.get_upcoming_activities(30)
database.get_fields()
database.get_crops_with_fields()
database.get_inventory()
results['all 5 queries serial (cold)'] = time.perf_counter() - t0

print("\n=== TIMING RESULTS ===")
for k, v in results.items():
    bar = '#' * int(v * 50)
    print(f"  {k:45s}  {v*1000:7.1f}ms  {bar}")
