

Project mostly based off https://github.com/helloflask/flask-examples/tree/main

### To setup the virtual environment
In the `flask-examples` directory:
```bash
python -m venv venv
. venv/Scripts/activate
pip install -r requirements.txt
```

For now I'm doing these updates manually
```bash
pip install flask
pip install pymongo
pip install pycryptodome
```

### Don't forget to create the config file.

### Also don't forget to whitelist the IP on mongodb.com

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
Here's an example of what the part that explains the file structure could look like. Inspired by https://github.com/imwilsonxu/fbone

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

## To-Do List

### 🔎 Implementaiton details
- [ ] Find art for each of the locations
- [ ] remove the locID from the leaderboard
- [ ] Make sure the welcome page shows a reminder to remember your Login Code
- [X] Make the leaderboard sort correctly
- [ ] Get a more logical favicon
- [X] flash messages

### 🗺️ User routes to make pleasant
- [X] When you visit a new location and you're logged in (display /location/LOCID page with a flashed message)
- [X] When you visit a location you've already discovered
- [ ] Make the settings read with more useful info

### 🚀 Deployment details
- [ ] How to make docker gud
- [ ] Make sure to check for any !todo or !security notes left behind