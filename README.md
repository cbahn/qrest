

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
├── requirements.txt
├── README.md
├── .gitignore
├── hello
│   ├── util_module.py
│   ├── test_mongo_module.py
│   ├── mongo_module.py
│   ├── crypto_module.py
│   ├── config.py.example
│   ├── app.py
│   ├── .flaskenv
│   ├── templates
│   │   │   ├── images
│   │   │   └── logo.svg
│   ├── static
│   │   └── data.js
│   ├── components
│   │   ├── app
│   │   │   ├── App.css
│   │   │   ├── App.jsx
│   │   │   └── App.test.js
│   │   └── index.js
│   ├── utils
│   │   ├── ...
│   │   └── index.js
│   ├── index.css
│   ├── index.js
│   ├── serviceWorker.js
│   └── setupTests.js
├── .gitignore
├── package.json
└── README.md
└── yarn.lock
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