import aiohttp
import asyncio


async def upload(url, filename):
    timeout = aiohttp.ClientTimeout(total=5)  # 10 seconds timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        form = aiohttp.FormData()
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    form.add_field("file", await resp.read(), filename=filename)
                    async with session.post(
                        "https://transfer.sh/", data=form
                    ) as response:
                        response_text = await response.text()
                        response_text = response_text.replace("\n", "")

                        # change it to get a direct link for the file
                        return response_text.replace(
                            "https://transfer.sh/", "https://transfer.sh/get/"
                        )
                else:
                    print("Failed to fetch the file")
        except asyncio.TimeoutError:
            print("Request timed out")
        except aiohttp.ClientError as e:
            print(f"Client error occurred: {e}")
