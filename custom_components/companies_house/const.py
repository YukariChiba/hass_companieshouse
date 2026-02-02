"""Global constants."""

import logging

DOMAIN = "companies_house"
_LOGGER = logging.getLogger(__package__)

# config keys
CONF_COMPANY_NUMBER = "company_number"
CONF_API_KEY = "api_key"
CONF_UPDATE_INTERVAL = "update_interval"

# default values
DEFAULT_UPDATE_INTERVAL = 720
API_BASE_URL = "https://api.company-information.service.gov.uk"

# required by Companies House developer guidelines
ATTRIBUTION = "Data provided by Companies House"
