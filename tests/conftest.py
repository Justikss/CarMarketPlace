import pytest
import pytest_asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher
import asyncio
import sys
sys.path.insert(0, '..')

from tests.mocked_bot import MockedBot


@pytest_asyncio.fixture(scope='session')
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()

@pytest.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()