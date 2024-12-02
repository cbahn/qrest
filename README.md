

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

## STRUCTURE (work in progress)
```

├── .gitignore
├── README.md
├── requirements.txt
└── hello
    ├── .flaskenv
    ├── app.py
    ├── config.py.example                   Example of how to format config.py file
    ├── crypto_module.py                    Utilites for encrypting and decrypting cookies
    ├── mongo_module.py                     Module for database access
    ├── static                              Static files
    │   ├── favicon.ico
    │   ├── favicon.pdn
    │   ├── favicon.png
    │   ├── pico_addons.css
    │   ├── place_error.png
    │   ├── place_img
    │   │   ├── dangan_map_404.jpg
    │   │   ├── golden-gulch.png
    │   │   ├── sad_panda_400x400.jpeg
    │   │   └── text.html
    │   └── style.css
    ├── templates                            Jinja2 templates
    │   ├── 404.html
    │   ├── TEST_qr.html
    │   ├── admin.html
    │   ├── index.html
    │   ├── layout.html
    │   ├── leaderboard.html
    │   ├── location.html
    │   ├── locations.html
    │   ├── login.html
    │   ├── my_location.html
    │   ├── new_adventurer.html
    │   ├── sad_panda.html
    │   ├── settings.html
    │   ├── unauth_layout.html
    │   ├── wait.html
    │   └── welcome.html
    ├── test_mongo_module.py
    └── util_module.py


```

## To-Do List

### 🔎 Implementaiton details
- [ ] Find art for each of the locations
- [X] remove the locID from the leaderboard
- [ ] Make sure the welcome page shows a reminder to remember your Login Code
- [X] Make the leaderboard sort correctly
- [ ] Get a more logical favicon
- [X] flash messages
- [ ] Admins shouldn't appear on the leaderboard
- [ ] fix new user server-side validation

### 🗺️ User routes to make pleasant
- [X] When you visit a new location and you're logged in (display /location/LOCID page with a flashed message)
- [X] When you visit a location you've already discovered
- [X] Make the settings better

### 🚀 Deployment details
- [ ] How to make docker gud
- [ ] Make sure to check for any !todo or !security notes left behind