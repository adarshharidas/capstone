# Customer API latency after a release
 
When customer API p95 latency increases immediately after a release, first
compare the release version with the last healthy version. Check dependency
latency, connection-pool saturation, database query time, and the health-check
results from the deployment platform.
 
If the p95 latency remains above the production threshold for three consecutive
checks, pause further rollout and initiate the rollback decision. A P1 incident
must be escalated to the network operations manager and the platform owner.