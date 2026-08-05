import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
import ssl

load_dotenv(Path(__file__).parent / '.env')

async def test():
    mongo_url = os.environ['MONGO_URL']
    
    # Try various SSL options
    configs = [
        {"url": mongo_url + "&tlsInsecure=true", "opts": {}},
        {"url": mongo_url, "opts": {"ssl": True, "ssl_cert_reqs": ssl.CERT_NONE}},
        {"url": mongo_url, "opts": {"tls": True, "tlsInsecure": True}},
    ]
    
    for cfg in configs:
        print(f"\nTrying: {cfg['opts'] or 'tlsInsecure in URL'}")
        try:
            client = AsyncIOMotorClient(cfg['url'], **cfg['opts'], serverSelectionTimeoutMS=10000)
            db = client[os.environ['DB_NAME']]
            result = await db.command('ping')
            print(f"  SUCCESS: {result}")
            await client.close()
            return
        except Exception as e:
            err = str(e)[:200]
            print(f"  FAILED: {err}")
    
    print("\nAll connection attempts failed")

asyncio.run(test())
