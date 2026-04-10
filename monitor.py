import asyncio
import requests
import os
from playwright.async_api import async_playwright

URL = "https://buyticketbrasil.com/evento/kornozfo?data=1778979600000&evento_local=1760655152236x555744260766826500"

PRECO_ALVO = 400

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


async def monitorar():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(5000)

        # abrir seletor tipo ingresso
        await page.locator("text=Tipo de ingresso").click()
        await page.wait_for_timeout(1000)

        # clicar em pista
        await page.locator("text=Pista").click()
        await page.wait_for_timeout(2000)

        # abrir seletor categoria
        await page.locator("text=Categoria").click()
        await page.wait_for_timeout(1000)

        # clicar em meia estudante
        await page.locator("text=Meia Estudante").click()
        await page.wait_for_timeout(3000)

        # pegar preço atualizado
        texto = await page.locator("body").inner_text()

        print(texto)

        preco = None

        for linha in texto.split("\n"):
            if "R$" in linha:
                try:
                    valor = (
                        linha.replace("R$", "")
                        .replace(".", "")
                        .replace(",", ".")
                        .strip()
                    )

                    preco = float(valor)
                    break
                except:
                    pass

        if preco is not None:
            print(f"Preço encontrado: R${preco}")

            if preco <= PRECO_ALVO:
                enviar_telegram(
                    f"⚠️ Ingresso Korn encontrado!\n"
                    f"Pista meia estudante: R${preco}\n"
                    f"{URL}"
                )
        else:
            print("Preço não encontrado.")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(monitorar())