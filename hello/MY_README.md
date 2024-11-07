

Project mostly based off https://github.com/helloflask/flask-examples/tree/main

### To setup the virtual environment
In the `flask-examples` directory:
```bash
python -m venv venv
. venv/Scripts/activate
pip install -r requirements.txt
```

For now I'm doing these updates manually
bash```
pip install flask
pip install pymongo
pip install pycryptodome
```

### Don't forget to create the config file.

### To run tests
```bash
pytest test_mongo_module.py
```

### Troubleshooting notes
I needed to install a python environmental thing
```bash
python -m pip install python-dotenv
```

