import asyncio

import httpx


async def test_auth_apis():
    base_url = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient() as client:
        # 测试登录
        print("\nTesting login...")
        login_data = {"username": "vben", "password": "123456"}
        response = await client.post(f"{base_url}/login", json=login_data)
        print(f"Login response: {response.status_code}")
        print(response.json())

        if response.status_code == 200:
            token = response.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}

            # 测试获取用户信息
            print("\nTesting get user info...")
            response = await client.get(f"{base_url}/getUserInfo", headers=headers)
            print(f"Get user info response: {response.status_code}")
            print(response.json())

            # 测试获取权限码
            print("\nTesting get permission codes...")
            response = await client.get(f"{base_url}/getPermCode", headers=headers)
            print(f"Get permission codes response: {response.status_code}")
            print(response.json())

        # 测试注册
        print("\nTesting register...")
        register_data = {
            "username": "testuser",
            "password": "testpass",
            "real_name": "Test User",
        }
        response = await client.post(f"{base_url}/register", json=register_data)
        print(f"Register response: {response.status_code}")
        print(response.json())


if __name__ == "__main__":
    asyncio.run(test_auth_apis())
