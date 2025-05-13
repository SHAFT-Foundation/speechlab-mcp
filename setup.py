from setuptools import setup

setup(
    name="speechlab_mcp",
    packages=["speechlab_mcp"],
    install_requires=["httpx", "python-dotenv", "mcp-api-client"],
) 