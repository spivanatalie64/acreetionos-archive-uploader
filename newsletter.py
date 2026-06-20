#!/usr/bin/env python3
"""Generate and send ISO release newsletter using opencode for AI content."""

import os
import subprocess
from datetime import datetime

import requests


def run_opencode(prompt: str) -> str:
    """Run opencode CLI with the given prompt.

    opencode looks for auth in $HOME/.local/share/opencode/auth.json.
    We write OPENCODE_AUTH_JSON there with 0600 perms, then wipe it.
    """
    opencode_bin = os.environ.get("OPENCODE_BIN", "npx --yes --package @opencode-ai/cli opencode")
    auth_json = os.environ.get("OPENCODE_AUTH_JSON")
    home = os.path.expanduser("~")
    opencode_data_dir = os.path.join(home, ".local", "share", "opencode")
    auth_file = os.path.join(opencode_data_dir, "auth.json")
    wrote_auth = False

    try:
        if auth_json:
            os.makedirs(opencode_data_dir, mode=0o700, exist_ok=True)
            with open(auth_file, "w") as f:
                f.write(auth_json)
            os.chmod(auth_file, 0o600)
            wrote_auth = True

        env = os.environ.copy()
        env["OPENCODE_NO_TELEMETRY"] = "1"

        result = subprocess.run(
            f'{opencode_bin} run {__import__("shlex").quote(prompt)}',
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
            shell=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"opencode exited {result.returncode}: {result.stderr[:500]}"
            )
        return result.stdout.strip()
    finally:
        if wrote_auth and os.path.isfile(auth_file):
            try:
                os.remove(auth_file)
            except OSError:
                pass


def generate_newsletter():
    """Generate ISO release newsletter using opencode CLI instead of Anthropic."""
    prompt = (
        "Write a newsletter email for AcreetionOS subscribers.\n\n"
        "AcreetionOS is a user-friendly Arch Linux distribution featuring "
        "the Cinnamon desktop, XLibre/X11 for stability, Pipewire audio, "
        "EXT4 filesystem, and a strong focus on privacy and system sovereignty. "
        "It is a rolling release distro that is beginner-friendly.\n\n"
        "The newsletter should announce that fresh ISO images (AcreetionOS 1.0 "
        "and AcreetionOS XL 1.0) have just been uploaded to the Internet Archive "
        "and SourceForge and are available for download.\n\n"
        "Guidelines:\n"
        "- Friendly, enthusiastic tone\n"
        "- Technical but accessible\n"
        "- 200-300 words\n"
        "- Start with 'Subject: ' on the first line\n"
        "- Leave a blank line after the subject before the body\n"
        "- Plain text, no markdown\n"
        "- End with download links placeholder text like: "
        "'Download now from the Internet Archive or SourceForge.'"
    )

    content = run_opencode(prompt)
    if not content:
        raise RuntimeError("opencode returned empty response")

    lines = content.split("\n")
    subject = "AcreetionOS - Fresh ISOs Now Available"
    body_start = 0

    for i, line in enumerate(lines):
        if line.startswith("Subject:"):
            subject = line.replace("Subject:", "").strip()
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).strip()
    return subject, body


def send_newsletter(subject, body):
    api_key = os.environ["BUTTONDOWN_API_KEY"]

    response = requests.post(
        "https://api.buttondown.email/v1/emails",
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "subject": subject,
            "body": body,
            "status": "about_to_send",
        },
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Buttondown error {response.status_code}: {response.text}")

    print(f"Newsletter sent: {subject}")


if __name__ == "__main__":
    subject, body = generate_newsletter()
    print(f"Subject: {subject}\n")
    print(body)
    send_newsletter(subject, body)
