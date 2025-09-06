## Tarmez-API

FastAPI server implementation in Python, which can help you host your own messaging application


### Quick start with docker
[Tarmez-Web installation guide](https://github.com/x3ron-ai/tarmez-web#quick-start-with-docker)

### Manual using
	git clone https://github.com/x3ron-ai/tarmez-server
	cd tarmez-server
	python3 -m venv env
	source env/bin/activate
	pip install -r requirements.txt
	cp .env.example .env
Then change `DATABASE_URL` and `SECRET_KEY` to yours values.
After all open alembic.ini and change `sqlalchemy.url` value to your `DATABASE_URL`.
Then use
```
    alembic upgrade head
```

[Web manual installation guide](https://github.com/x3ron-ai/tarmez-web#manual-using)
#### Run application
	uvicorn app.main:app --host 0.0.0.0 --port 8000