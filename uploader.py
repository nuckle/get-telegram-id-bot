import aiohttp


async def upload(url, filename):
    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        async with session.get(url) as resp:
            if resp.status == 200:
                form.add_field('file', await resp.read(), filename=filename)
                async with session.post('https://transfer.sh/', data=form) as response:
                    response_text = await response.text()
                    response_text = response_text.replace("\n", "")

                    # change it to get a direct link for the file
                    return response_text.replace('https://transfer.sh/', 'https://transfer.sh/get/')
            else:
                print('Failed to fetch the file')
