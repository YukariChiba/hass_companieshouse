# UK Companies House Integration for Home Assistant

A custom integration for Home Assistant that tracks company information from the UK Companies House Public Data API.

## Configuration

### Obtain API Key

- Register at [Companies House Developer Hub](https://developer.company-information.service.gov.uk/).
- Create an application.
- Create and copy your **REST API Key**.

### Create Integration

- Go to **Settings** > **Devices & Services**.
- Click **Add Integration**.
- Search for **Companies House**.
- Enter the following configs:
   - **API Key**: The key you generated above.
   - **Company Number**: The 8-digit company number (e.g., `11451419`).
   - **Update Interval**: How often to fetch data in minutes (default is 60).
