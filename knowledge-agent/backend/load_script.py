import asyncio  
from app.db.session import AsyncSessionLocal  
from app.knowledge.loader import load_json, load_csv  
from pathlib import Path  
async def main():  
    async with AsyncSessionLocal() as session:  
        j = await load_json(session, Path('data/sample.json'))  
        c = await load_csv(session, Path('data/sample.csv'))  
        await session.commit()  
        print('Loaded JSON:', j, 'CSV:', c)  
if __name__ == '__main__':  
    asyncio.run(main())  
