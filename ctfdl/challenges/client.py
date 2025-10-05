from ctfbridge import create_client


async def get_authenticated_client(url: str, username=None, password=None, token=None):
    client = await create_client(url)

    if username and password:
        await client.auth.login(username=username, password=password)
    elif token:
        await client.auth.login(token=token)
    else:
        pass

    return client
