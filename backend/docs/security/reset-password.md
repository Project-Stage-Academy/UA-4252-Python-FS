# 1. Token Time-To-Live (TTL) Policy

## JWT (JSON Web Tokens)
* **Access Token TTL:** 1 hour
* **Refresh Token TTL:** 1 day

## Other Tokens
* **Email Verification:** A standard Django token is used for sending email verification links.

# 2. Email Provider Configuration

## Development Environment
* **Provider:** MailHog
* **Setup:** Used via Docker.

## Production Environment
* **Status:** No email provider has been configured for production yet.

# 3. CORS and Auth Notes

## CORS (Cross-Origin Resource Sharing)
* **Current Policy:** The project is configured with `CORS_ALLOW_ALL_ORIGINS = True` in `settings.py`.

## Authentication Tokens
* **Primary Auth:** JWT is used for user authentication.
* **Email Verification:** Django's built-in token is used for this specific flow.

# 4. Monitoring and Alerting

* Standard application logging is in place.

* No specific alerting infrastructure for password reset abuse has been specified.

# 5. Incident Runbook (Token Revocation)

This document covers the current capabilities for responding to incidents.

## Token Revocation
* **Mechanism:** A "logout" endpoint is implemented.
* **Action:** When a user logs out, their JWT is actively blacklisted, invalidating it for future use.
