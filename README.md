[![Release 1.8.0](https://img.shields.io/badge/release-1.8.0-blue.svg)](https://github.com/trellixio/trellis-template/tree/fastapi)
[![Python 3.12](https://img.shields.io/badge/python-3.12-yellow.svg)](https://www.python.org/downloads/release/python-312/)
[![MongoDB 7.0](https://img.shields.io/badge/mongodb-7.0-green.svg)](https://www.mongodb.com/docs/v7.0/)


# Trellis Instagram

This is instagram integration with Beans


> ℹ️ At Beans, an integration with a third party application is referred to as a **Trellis**.


This project is made with FastAPI
The technologies used for this project are:
- [FastAPI](https://fastapi.tiangolo.com/) as web framework
- [MongoDB](https://www.mongodb.com/docs/) as database
- [Beanie](https://roman-right.github.io/beanie/) as ODM
- [Pytest](https://docs.pytest.org/) as testing framework
- [Github Actions](https://docs.github.com/en/actions) for workflow automation
- [Render](https://render.com/) as cloud platform for deployment


## 🔨 Installing

### Python 3.12
Before getting started, ensure that [Python 3.12](https://www.python.org/) is installed on your computer.

### MongoDB
MongoDB is a document-oriented database that use JSON-like documents to store data.
You will need to install MongoDB 6.0 [locally](https://www.mongodb.com/docs/manual/installation/)
or sign up for a free hosted one with [MongoDB Atlas](https://www.mongodb.com/pricing).
Once you install MongoDB, make sure to create a database.

### Steps
Clone the repo and open a terminal at the root of the cloned repo.

1. Setup a virtual env. Only do this on your first run.
```shell
python3.12 -m venv .venv
```

2. Activate the virtualenv
```shell
source .venv/bin/activate
```

3. Install all dependencies:
```shell
pip install -r requirements-dev.txt
```

4. Set up pre-commit
```shell
pre-commit install
```

Allow pre-commit custom hooks execution
```shell
git update-index --chmod=+x scripts/*
```

5. Init environment variables. Duplicate the env template file:
```shell
cp ./.env.tpl ./.env
```
Open `.env` file with a text editor and update the env vars as needed


## ⏯ Running

To run the app on your machine, make sure to have activated your virtualenv and run:
```shell
python main.py
```

- Visit: http://127.0.0.1:8000/ to view the application running in your browser
- Visit: http://127.0.0.1:8000/instagram/ to view the instagram application


## 🖌 Formatting

Keep in mind that those are automated formatting assistant tools.
They will not always give the best result, as they just apply
rules blindly. As a developer you still have the responsibility to
ensure that the code is formatted with perfection.

- Use black to format the code
From the project root run:
```shell
black .
```

- Use isort to sort the import
From the project root run:
```shell
isort .
```


## 🧽 Linting

Linters are useful to ensure that your code quality matches with standards.

- Running pre-commit on the project to run all linters.
```shell
pre-commit run --all-files
```

- Use pylint to check for common mistakes.
From the project root, run:
```shell
pylint AppMain trellis tests
```

- Use mypy to check for typing issues.
From the project root, run:
```shell
mypy .
```

- Use mypy to check for documentation issues.
From the project root, run:
```shell
pydocstyle .
```


## 🧪 Testing

Tests are run using the pytest library.
From the project root, run:
```shell
pytest
```

## Local dev

### SSL
To run the project locally you may need to setup SSL certificates in order to use HTTPS on localhost. First follow [this step by step guide](https://web.dev/how-to-use-local-https/) to set up [mkcert](https://github.com/FiloSottile/mkcert). Once you are done update the env vars `APP_SETTINGS_SSL_KEYFILE` and `APP_SETTINGS_SSL_CERTFILE` with path to your cert files.


## 🚀 Deploying

[Render](https://docs.render.com/) is a very easy to use cloud platform to host your python project.
Simply follow the [step by step guide](https://docs.render.com/deploy-fastapi) to deploy your project.
