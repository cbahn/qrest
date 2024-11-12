

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

## STRUCTURE
Here's an example of what the part that explains the file structure could look like

## STRUCTURE

    ├── CHANGES                     Change logs
    ├── README.markdown
    ├── fabfile.py                  Fabric file to automated managament project
    ├── fbone.conf                  Apache config
    ├── requirements.txt            3rd libraries
    ├── tests.py                    Unittests
    ├── wsgi.py                     Wsgi app
    ├── fbone
       ├── __init__.py
       ├── app.py                   Main App
       ├── config.py                Develop / Testing configs
       ├── constants.py             Constants
       ├── decorators.py            Customized decorators
       ├── extensions.py            Flask extensions
       ├── filters.py               Flask filters
       ├── utils.py                 Python utils
       ├── frontend                 Frontend blueprint
       │   ├── __init__.py
       │   ├── forms.py             Forms used in frontend modular
       │   ├── views.py             Views used in frontend modular
       ├── user
       ├── api
       ├── static                   Static files
       │   ├── css
       │   ├── favicon.png
       │   ├── humans.txt
       │   ├── img
       │   ├── js
       │   └── robots.txt
       └── templates                Jinja2 templates
           ├── errors
           ├── frontend
           ├── index.html
           ├── layouts              Jinja2 layouts
           │   ├── base.html
           │   └── user.html
           ├── macros               Jinja2 macros
           ├── mails                Mail templates
           └── user
