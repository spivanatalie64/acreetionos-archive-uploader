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
---

## 🤖 Pullfrog AI Review

This repository uses **Pullfrog AI** to automatically review pull requests.

Pullfrog is an AI-powered code review agent that analyzes every PR for code quality,
security issues, performance problems, and best practice violations. Reviews appear
as inline PR comments and checks. Trigger manually by commenting `@pullfrog` on any PR.

Powered by OpenRouter.