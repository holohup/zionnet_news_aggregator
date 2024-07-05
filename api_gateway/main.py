from fastapi import FastAPI


from schema import RegistrationRequest


app = FastAPI()


@app.post('/register')
async def register_new_user(request: RegistrationRequest):
    return {'result': 'ok'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8000)
