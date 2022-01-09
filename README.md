# Shopify 2022 Infrastructure Engineering Internship Project

## Get Started

1. Set up a Python virtual environment: `python -m venv [name of venv]`
2. Activate virtual environment: `source [name of venv]/bin/activate`
3. Install requirements: `pip install requirements.txt`
4. Export Flask app: `export FLASK_APP=app`
5. Run Flask: `flask run`
6. Navigate to link on Terminal results e.g. `127.0.0.5000`

## Documentation

### class `InventoryModel`

#### `__init__(item_id, item_name, stock)`

##### Parameters:

* `item_id`: `UNIQUE` integer
* `item_name`: string
* `stock`: integer

#### `__repr__()`

##### Returns: 

* String of the form `"id #[item_id] - [item_name] - [stock] left"`






