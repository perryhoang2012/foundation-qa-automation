# API Test Project with Python & Playwright

## Set Up

```bash
python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
playwright install
```

## Run Test

### Run all tests
```bash
pytest
```

### Run one test
```bash
pytest tests/test_landscape_generator.py
```

## Folder examples

- `tests/test_api_example.py`: Examples of test API with requests from Playwright.
- `pytest.ini`: Configure pytest.
- `requirements.txt`: Required packages
