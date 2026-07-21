# School Holiday Sensor for Home Assistant

This integration creates a sensor that is `True` during selected school holiday periods based on country and region data loaded from local YAML files.

## Features

- Selectable country and region via config flow
- Custom YAML holiday definitions (no cloud dependency)
- Sensor state is `True`/`False` during configured holiday periods
- Attributes include current holiday name and upcoming holidays
- Community-contributable holiday files

## How to Install

1. Go to Home Assistant → HACS → Integrations.
2. Click the three-dot menu → **Custom Repositories**.
3. Add this repository URL:
   ```
   https://github.com/bsmeding/home_assistant_school_holiday_sensor
   ```
   as an **Integration**.
4. Search for `School Holiday Sensor` in HACS and install it.
5. Restart Home Assistant.
6. Go to Settings → Devices & Services → Add Integration → Search for **School Holiday Sensor**.
7. Select your country and region.

---

## Contributing

We welcome community contributions to expand holiday data for more countries or update existing entries.

### To Add a New Country:

1. Navigate to `custom_components/school_holiday_sensor/holidays/`.
2. Create a new file named `<cc>.yaml` where `<cc>` is the ISO 2-letter country code, e.g., `de.yaml` for Germany.
3. Structure the file like this:

```yaml
# source: https://example.org/official-holiday-site
- name: Region Name
  holidays:
    - name: Holiday Name
      date_from: DD-MM-YYYY
      date_till: DD-MM-YYYY
```

### To Update Existing Holidays:

- Edit the relevant `<country>.yaml` file.
- Keep existing regions in place if possible.
- Make sure new holidays use the correct format.

> **Note**: Dates may use `DD-MM-YYYY` or `YYYY-MM-DD`. Inclusive ranges: `date_till` is the last holiday day.

### Submitting a Pull Request

1. Fork the repository.
2. Commit your changes to a new branch.
3. Open a pull request with a brief description and source links for the added/updated data.

### Local validation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pyyaml
python scripts/validate_files.py
```

Let’s build a global library of school holidays together!
