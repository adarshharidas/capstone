# Deployment health-check failure
 
A completed deployment with a failed health check is not considered healthy.
Inspect application logs, readiness probes, downstream dependencies, and the
deployment diff. If the failure is release-specific, stop promotion and use
the last known healthy build while the team investigates.
 
Record the deployment ID, release version, failed check, and operator decision
in the incident report for stakeholder visibility.
 