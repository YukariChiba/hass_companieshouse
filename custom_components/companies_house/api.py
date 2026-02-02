"""API client to Companies House API."""

import asyncio

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import _LOGGER, API_BASE_URL


class CompaniesHouseApiClient:
    """API Client."""

    def __init__(self, hass: HomeAssistant, api_key: str) -> None:
        """Initialize API Client (create session, store api key)."""
        self._api_key = api_key.strip()
        self._session = async_get_clientsession(hass)

    def _raise_error(self, error_code: str) -> None:
        """Raise a ValueError (helper to avoid TRY301)."""
        raise ValueError(error_code)

    async def get_company_profile(self, company_number: str) -> dict:
        """Get company profile JSON."""
        company_number = company_number.strip().upper()
        url = f"{API_BASE_URL}/company/{company_number}"
        auth = aiohttp.BasicAuth(self._api_key, "")

        try:
            async with asyncio.timeout(10.0):
                response = await self._session.get(url, auth=auth)

                if response.status == 401:
                    _LOGGER.error("Companies House API: Unauthorized (Check API Key)")
                    self._raise_error("invalid_auth")

                if response.status == 404:
                    _LOGGER.error(
                        "Companies House API: Company %s not found", company_number
                    )
                    self._raise_error("company_not_found")

                if response.status == 400:
                    _LOGGER.error("Companies House API: Bad Request")
                    self._raise_error("bad_request")

                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientResponseError as err:
            _LOGGER.error("HTTP error fetching company profile: %s", err.status)
            raise ValueError("api_error") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error fetching data: %s", err)
            raise ValueError("connection_error") from err
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise ValueError("unknown_error") from err
