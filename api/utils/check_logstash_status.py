# -*- coding: utf-8 -*-
import sys

import httpx


def check_logstash_agent_status() -> bool:
    """
    Check for logstash_agent status
    """
    try:
        response = httpx.get("http://logstash_agent:9600")

        if response.status_code != 200:
            return False

        status = response.json().get("status")

        if status != "green":
            return False

        return True
    except httpx.ConnectError:
        return False


def main() -> None:
    if check_logstash_agent_status():
        sys.stdout.write("1")
    else:
        sys.stdout.write("0")


if __name__ == "__main__":
    main()
