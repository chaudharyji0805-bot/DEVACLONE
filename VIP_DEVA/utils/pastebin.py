import aiohttp
import socket
from asyncio import get_running_loop
from functools import partial

# ---------- 1) ezup.dev (socket paste) ----------
def _netcat(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(content.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096).decode("utf-8").strip("\n\x00")
        if not data:
            break
        return data
    s.close()


async def paste(content: str):
    loop = get_running_loop()
    link = await loop.run_in_executor(None, partial(_netcat, "ezup.dev", 9999, content))
    return link


# ---------- 2) Pastebin API via aiohttp ----------
async def INNOCENTBin(content: str):
    url = "https://pastebin.com/api/api_post.php"
    data = {
        "api_dev_key": "9Rfu50iV5l3EuRWATw7EDLuC37RED-C4",
        "api_paste_code": content,
        "api_option": "paste",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            return await resp.text()


# ---------- 3) DEVABin wrapper (fixes ImportError) ----------
class DEVABin:
    """
    Compatible interface for code that does:
    from VIP_DEVA.utils.pastebin import DEVABin
    and then calls: await DEVABin.paste(text)
    """

    @staticmethod
    async def paste(content: str) -> str:
        if not content:
            return "Empty content."

        # avoid huge payloads
        if len(content) > 40000:
            content = content[:40000] + "\n\n[TRUNCATED]"

        # Try ezup first (fast)
        try:
            link = await paste(content)
            if link:
                return link
        except Exception:
            pass

        # Fallback to pastebin
        try:
            link = await INNOCENTBin(content)
            if link:
                return link.strip()
        except Exception:
            pass

        # last fallback: return snippet
        return content[:3500]


# Optional aliases (if other files import these names)
DevaBin = DEVABin
PasteBin = DEVABin
