import asyncio
import os
import requests
from playwright.async_api import async_playwright

URL = "https://buyticketbrasil.com/evento/kornozfo?data=1778979600000&evento_local=1760655152236x555744260766826500"
PRECO_ALVO = 400

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Telegram não configurado.")
        return

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=15)
        print("Mensagem enviada no Telegram.")
    except Exception as e:
        print("Erro Telegram:", e)


async def monitorar():
    enviar_telegram("🤖 Bot BuyTicket iniciado.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print("Abrindo página...")
            await page.goto(URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)

            print("Abrindo filtro de tipo...")
            await page.locator("text=Tipo de ingresso").click()
            await page.wait_for_timeout(1500)

            print("Selecionando Pista...")
            await page.get_by_text("Pista", exact=True).click()
            await page.wait_for_timeout(3000)

            print("Abrindo filtro de categoria...")
            await page.locator("text=Categoria").click()
            await page.wait_for_timeout(1500)

            print("Selecionando Meia Estudante...")
            await page.get_by_text("Meia Estudante", exact=True).click()
            await page.wait_for_timeout(5000)

            texto = await page.locator("body").inner_text()

            print("=== TEXTO FILTRADO ===")
            print(texto[:5000])

            preco_encontrado = None

            for linha in texto.split("\n"):
                linha = linha.strip()

                if linha.startswith("R$"):
                    try:
                        valor = (
                            linha.replace("R$", "")
                            .replace(".", "")
                            .replace(",", ".")
                            .strip()
                        )

                        preco = float(valor)

                        if preco_encontrado is None or preco < preco_encontrado:
                            preco_encontrado = preco

                    except:
                        pass

            if preco_encontrado is not None:
                print(f"Preço encontrado: R$ {preco_encontrado:.2f}")

                if preco_encontrado <= PRECO_ALVO:
                    mensagem = (
                        f"⚠️ Ingresso Korn encontrado!\n"
                        f"Pista meia estudante: R$ {preco_encontrado:.2f}\n"
                        f"{URL}"
                    )
                    enviar_telegram(mensagem)
                else:
                    print("Preço acima do alvo.")
            else:
                print("Nenhum preço encontrado após filtro.")

        except Exception as e:
            print("Erro durante monitoramento:", e)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(monitorar())