# AcreetionOS Archive Uploader

Automatically uploads AcreetionOS ISO files to the Internet Archive once a week.

## ISOs

- `AcreetionOS-1.0-x86_64.iso`
- `AcreetionOS_XL-1.0-x86_64.iso`

## Schedule

Runs every Monday at 00:00 UTC. Can also be triggered manually via `workflow_dispatch`.

## Secrets required

| Secret | Description |
|--------|-------------|
| `IA_ACCESS_KEY` | Internet Archive S3 access key |
| `IA_SECRET_KEY` | Internet Archive S3 secret key |
