# Nimbus Platform: Secrets Management

## Where secrets live
All passwords, API keys, and certificates are stored in Nimbus Vault. Never put secrets in Git, in `.env` files, or in container images. The security scan blocks any deployment that contains a hard-coded secret.

## Using a secret in your app
Reference the secret in your `nimbus.yaml` under `secrets:`. The platform injects it into the container as a file under `/vault/secrets/` at start-up. Your app should read the file, not an environment variable.

## Rotation
Secrets must be rotated at least every 90 days. Nimbus Vault emails the service owner 14 days before a secret expires. Database passwords are rotated automatically every 30 days.

## Leaked secret
If a secret is exposed, rotate it immediately in Nimbus Vault and raise a P2 security incident, even if you think nobody used it.
