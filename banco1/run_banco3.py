import uvicorn

from bank_instances import configure_bank_environment


BANK = configure_bank_environment("banco3")


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=BANK["api_port"], reload=True)
