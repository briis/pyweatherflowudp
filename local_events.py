from pyweatherflowudp.client import WeatherFlowListner
from pyweatherflowudp.const import UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC
import asyncio
import logging


_LOGGER = logging.getLogger(__name__)

STATION_ID = "MY STATION"
IPADDRESS = "0.0.0.0"
PORT = 50222

def cleanup():
    asyncio.ensure_future(_async_cleanup())

async def _async_cleanup():
    tasks = [task for task in asyncio.Task.all_tasks() if task != asyncio.Task.current_task()]    
    for task in tasks:
        task.cancel()
    # further cleanup
    # raise AbnormalTermination()

async def devicedata():

    logging.basicConfig(level=logging.DEBUG)

    # Log in to Unifi Protect
    wfl = WeatherFlowListner(
        STATION_ID,
        IPADDRESS,
        PORT,
        UNIT_SYSTEM_METRIC
    )

    await wfl.update()
    unsub = wfl.subscribe_udpsocket(subscriber)

    for i in range(60):
        await asyncio.sleep(1)

    # Close the Session
    await wfl.async_disconnect_socket()
    unsub()


def subscriber(updated):
    _LOGGER.info("Subscription: updated=%s", updated)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(devicedata())
    loop.close()
except KeyboardInterrupt:
    print('\nApplication shutdown by user')
