"""HomeWizard Energy API library."""

from aiohttp import ClientSession

from .errors import DisabledError, InvalidStateError, RequestError, UnsupportedError
from .v1 import HomeWizardEnergyV1
from .v2 import HomeWizardEnergyV2

__all__ = [
    "DisabledError",
    "HomeWizardEnergyV1",
    "HomeWizardEnergyV2",
    "InvalidStateError",
    "RequestError",
    "UnsupportedError",
]


async def has_v2_api(host: str, websession: ClientSession | None = None) -> bool:
    """Check if the device has support for the v2 api."""
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        # v2 api is https only and returns a 401 Unauthorized when no key provided,
        # no connection can be made if the device is not v2
        url = f"https://{host}/api"
        async with websession.get(
            url, ssl=False, raise_for_status=False, timeout=15
        ) as res:
            return res.status == 401
    except Exception:  # pylint: disable=broad-except
        # all other status/exceptions means the device is not v2 or not reachable at this time
        return False
    finally:
        if not websession_provided:
            await websession.close()


def get_verification_hostname(model: str, serial_number: str) -> str:
    """Get the verification name for the device."""
    model_map = {
        "HWE-P1": "p1dongle",
        "HWE-SKT": "energysocket",
        "HWE-WTR": "watermeter",
        "HWE-DSP": "display",
        "HWE-KWH1": "energymeter",
        "SDM230-wifi": "energymeter",
        "HWE-KWH3": "energymeter",
        "SDM630-wifi": "energymeter",
        "HWE-BAT": "battery",
    }

    if model not in model_map:
        raise ValueError(f"Unsupported model: {model}")

    return f"appliance/{model_map[model]}/{serial_number}"
