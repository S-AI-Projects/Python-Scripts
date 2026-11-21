from datetime import datetime as dt


# Run as root to modify the system hosts file.
hosts_path = "/etc/hosts"
redirect = "127.0.0.1"
website_list = [
    "www.facebook.com",
    "facebook.com",
    "dub119.mail.live.com",
    "www.dub119.mail.live.com",
    "www.gmail.com",
    "gmail.com",
]


def remove_blocked_websites(lines):
    return [
        line
        for line in lines
        if not any(website in line for website in website_list)
    ]


def main():
    while True:
        now = dt.now()
        work_start = dt(now.year, now.month, now.day, 8)
        work_end = dt(now.year, now.month, now.day, 16)

        if work_start < now < work_end:
            print("Working hours...")
            with open(hosts_path, "r+") as hosts_file:
                content = hosts_file.read()
                for website in website_list:
                    if website not in content:
                        hosts_file.write(f"{redirect} {website}\n")
        else:
            with open(hosts_path, "r+") as hosts_file:
                content = hosts_file.readlines()
                hosts_file.seek(0)
                for line in remove_blocked_websites(content):
                    hosts_file.write(line)
                hosts_file.truncate()


if __name__ == "__main__":
    main()
