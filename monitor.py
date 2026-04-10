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
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)


async def monitorar():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(URL, wait_until="networkidle")

        await page.wait_for_timeout(5000)

        texto = await page.locator("body").inner_text()

        linhas = texto.split("\n")

        menor_preco = None

        for i, linha in enumerate(linhas):
            linha_lower = linha.lower()

            if "pista" in linha_lower and "meia" in linha_lower:
                for j in range(i, min(i + 8, len(linhas))):
                    if "R$" in linhas[j]:
                        preco_texto = (
                            linhas[j]
                            .replace("R$", "")
                            .replace(".", "")
                            .replace(",", ".")
                            .strip()
                        )

                        try:
                            preco = float(preco_texto)

                            if menor_preco is None or preco < menor_preco:
                                menor_preco = preco
                        except:
                            pass

        if menor_preco is not None:
            print(f"Menor preço encontrado: R${menor_preco}")

            if menor_preco <= PRECO_ALVO:
                enviar_telegram(
                    f"⚠️ Ingresso Korn encontrado!\n"
                    f"Pista meia estudante: R${menor_preco}\n"
                    f"{URL}"
                )
        else:
            print("Nenhum ingresso encontrado.")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(monitorar())