# Network inventory sync failure
 
For a network inventory sync failure, inspect schema validation errors and the
device adapter response. Compare the current schema with the contract expected
by the inventory worker. A staging failure should be fixed before production
promotion, but does not require a production outage escalation by itself.