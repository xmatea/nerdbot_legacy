import io
import asyncio
from pyppeteer import launch

async def convert_to_img(html: str) -> io.BytesIO:
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


#remove from here down, just for testing
if __name__ == "__main__":
	from PIL import Image

	html = """
		<div style="width:250px; height:250px; background-color: #AA00AA"></div>
	"""

	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	img = loop.run_until_complete(convert_to_img(html))

	Image.open(img).show()