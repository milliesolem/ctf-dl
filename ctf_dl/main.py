import argparse
import os
from urllib.parse import unquote, urlparse

import requests
from ctfbridge import get_client


def download_challenges(base_url, username, password, token, output_dir):
    client = get_client(base_url)

    if username and password:
        client.login(username=username, password=password)
    elif token:
        client.login(token=token)
    else:
        raise ValueError("You must provide either both username and password, or a token to log in.")

    challenges = client.get_challenges()

    os.makedirs(output_dir, exist_ok=True)

    for chal in challenges:
        print(f"[{chal.category}] {chal.name} ({chal.value} points)")

        # Save challenge to a text file
        chal_dir = os.path.join(output_dir, chal.category, chal.name)
        os.makedirs(chal_dir, exist_ok=True)

        chal_filename = os.path.join(chal_dir, "README.md")
        with open(chal_filename, "w", encoding="utf-8") as f:
            f.write(f"# {chal.name}\n\n")
            f.write(f"**Category:** {chal.category}\n\n")
            f.write(f"**Points:** {chal.value}\n\n")
            f.write(f"## Description\n\n{chal.description}\n\n")
            
            # If there are attachments, list them
            if chal.attachments:
                f.write("## Attachments\n\n")
                for attachment in chal.attachments:
                    attachment_name = unquote(urlparse(attachment).path.split("/")[-1])
                    attachment_path = os.path.join(chal_dir, attachment_name)

                    # Download the file
                    r = requests.get(attachment)
                    with open(attachment_path, 'wb') as af:
                        af.write(r.content)

                    # Add attachment link in markdown
                    f.write(f"- [{attachment_name}]({attachment_name})\n")
        

def main():
    parser = argparse.ArgumentParser(description="Download all CTF challenges easily.")
    parser.add_argument("--url", required=True, help="Base URL of the CTF platform (e.g., https://demo.ctfd.io)")
    parser.add_argument("--username", required=False, help="Username for login")
    parser.add_argument("--password", required=False, help="Password for login")
    parser.add_argument("--token", required=False, help="Token for login")
    parser.add_argument("--output", default="challenges", help="Output directory to save challenges")

    args = parser.parse_args()

    if args.token:
        if args.username or args.password:
            parser.error("Provide either --token or --username and --password, not both.")
    elif args.username and args.password:
        pass
    else:
        parser.error("You must provide either --token or both --username and --password.")

    download_challenges(args.url, args.username, args.password, args.token, args.output)

if __name__ == "__main__":
    main()

