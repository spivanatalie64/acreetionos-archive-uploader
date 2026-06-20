#!/usr/bin/env python3
"""Generate and send ISO release newsletter using opencode for AI content."""

import os
import json
import subprocess
from datetime import datetime

import requests


def run_opencode(prompt: str) -> str:
    """Run opencode CLI with the given prompt.

    opencode looks for auth in $HOME/.local/share/opencode/auth.json.
    We write OPENCODE_AUTH_JSON there with 0600 perms, then wipe it.
    """
    opencode_bin = os.environ.get("OPENCODE_BIN", "opencode")
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
            [opencode_bin, "run", prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
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
    """Post newsletter to the website repo via GitHub API instead of email."""
    website_repo = "acreetionos-code/acreetionos-code.github.io"
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"newsletters/iso-release-{date_str}.json"

    entry = {
        "date": date_str,
        "subject": subject,
        "body": body,
        "type": "iso_release",
    }

    headers = {
        "Authorization": f"token {os.environ['GH_PAT']}",
        "Accept": "application/vnd.github+json",
    }

    check = requests.get(
        f"https://api.github.com/repos/{website_repo}/contents/{filename}",
        headers=headers,
    )
    sha = check.json().get("sha") if check.status_code == 200 else None

    import base64 as _b64
    payload = {
        "message": f"newsletter: add ISO release {date_str}",
        "content": _b64.b64encode(json.dumps(entry, indent=2).encode()).decode(),
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(
        f"https://api.github.com/repos/{website_repo}/contents/{filename}",
        headers=headers,
        json=payload,
    )

    if response.status_code not in (200, 201):
        raise Exception(f"GitHub API error {response.status_code}: {response.text}")

    print(f"Newsletter posted to website: {filename}")


if __name__ == "__main__":
    subject, body = generate_newsletter()
    print(f"Subject: {subject}\n")
    print(body)
    send_newsletter(subject, body)
