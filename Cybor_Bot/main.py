from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path
from AI_bot import AI_BOT


app = FastAPI()
bot = AI_BOT()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)


def bott():
    df = bot.read_data()
    bot.input_data_for_encoder(df)
    bot.input_data_for_decoder(df)
    bot.output_data_for_decoder()
    bot.setup_encoder_decoder_data()


templates = Jinja2Templates(directory="/home/sasai/Downloads/Cybor_Bot/templates")

# bot.train_model("128","2")
i = 0


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    bott()
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/get")
def get_bot_response(msg: str):
    answer = ""
    try:

        answer = bot.predict_output(msg)
    except:
        answer = (
            "This question is out of my knowledge.....Please wait for my new version"
        )

    return str(answer)


if __name__ == "__main__":
    uvicorn.run("main:app")
