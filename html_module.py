import io
import asyncio
from pyppeteer import launch

async def html_to_img(html: str) -> io.BytesIO:
	browser = await launch()
	page = await browser.newPage()
	await page.setContent(html)
	cont_html = await page.content()

	# insert div containing all content of body and scale
	cont_html = cont_html.replace("<body>", "<body style='background-color:#36393E;color:white;'><div id='nerdbotcontainer' style='display:inline-block;margin:0;padding:0;'>")
	cont_html = cont_html.replace("</body>", "</div></body>")

	await page.setContent(cont_html)

	content = await page.J("#nerdbotcontainer")
	image = io.BytesIO(await content.screenshot())
	await browser.close()

	return image


async def url_to_img(url: str) -> io.BytesIO:
	browser = await launch()
	page = await browser.newPage()
	await page.goto(url)

	image = io.BytesIO(await page.screenshot())
	await browser.close()

	return image