import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

async def test():
    mongo_url = os.environ['MONGO_URL']
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_url, tlsAllowInvalidCertificates=True)
    db = client[os.environ['DB_NAME']]
    try:
        result = await db.command('ping')
        print(f"MongoDB ping: {result}")
    except Exception as e:
        print(f"MongoDB error: {e}")
    finally:
        await client.close()

asyncio.run(test())
