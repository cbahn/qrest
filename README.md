

## Development

Set an environmental variable for your mongo connection string
```
MONGO_URI=mongodb://
```

Create a python virtual environment
```bash
python -m venv venv
. \venv\Scripts\activate
```

Install python dependencies
```bash
python -m pip install -r .\requirements.txt
```

to run
```
python .\run.py
```

## Docker

Port 8080 should be mapped to something

a volume should be mounted to `/app/marino/static/uploads`