import sys
import httpx


python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

url = 'https://tls.browserleaks.com/json'

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            response_text = response.text

            file_name = f"results/python_httpx-{python_version}.json"

            with open(file_name, 'w') as file:
                file.write(response_text)

        else:
            print(f"Ошибка при выполнении запроса: {response.status_code}")

if __name__ == '__main__':
    import sys
    import asyncio

    asyncio.run(main())
