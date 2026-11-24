# FinTech security baseline

This local policy gives the requirements agent a baseline when a stakeholder
does not name a specific regulation.

- Default to least privilege, strong authentication, and explicit session
  timeout requirements.
- Encrypt sensitive data in transit and at rest, and keep secrets out of source
  code and logs.
- Validate inputs, protect against injection, and record security-relevant
  events without logging raw PII or credentials.
- Define recovery, backup, monitoring, and incident-response requirements for
  critical financial services.
- Require human review for compliance mappings and high-risk AI-generated
  recommendations.
