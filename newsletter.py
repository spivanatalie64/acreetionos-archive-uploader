#!/usr/bin/env python3
import os
import anthropic
import requests

def generate_newsletter():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
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
            }
        ]
    )

    content = message.content[0].text.strip()
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
