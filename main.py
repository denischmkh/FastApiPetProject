import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from auth.router import router as auth_router
from products.router import router as products_router
from fastapi.staticfiles import StaticFiles
from auth.exceptions import RegisterException, LoginException

app = FastAPI()

app.include_router(auth_router)
app.include_router(products_router)

app.mount('/styles', StaticFiles(directory='./styles'), name='styles')


@app.exception_handler(RegisterException)
async def register_error(request: Request, exc: RegisterException):
    return RedirectResponse(url='/auth/register', status_code=303)

@app.exception_handler(LoginException)
async def login_error(request: Request, exc: LoginException):
    return RedirectResponse(url='/auth/login', status_code=303)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    try:
        uvicorn.run("main:app", reload=True, workers=4, log_level=logging.INFO)
    except KeyboardInterrupt:
        logging.info("Program Closed")