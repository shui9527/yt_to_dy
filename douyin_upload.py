import configparser
import asyncio
from playwright.async_api import async_playwright


async def upload_video(video_path, video_name, description, tags, storage_state, headless):
    platform = '抖音'
    config = configparser.ConfigParser()
    with open('config.ini', encoding='utf-8') as f:
        config.read_file(f)
        storage_state = config.get('Douyin', 'cookie_path')
        storage_state = storage_state + config.get('Douyin', 'phone') + '.json'

    async with async_playwright() as playwright:
        print(platform + ": 登陆中")
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(storage_state=storage_state)
        page = await context.new_page()



        await page.goto(config.get('Douyin', 'up_site'))
        await page.wait_for_url(config.get('Douyin', 'up_site'))

        print(platform + ": 登陆成功")

        await page.locator(".upload-btn--9eZLd").set_input_files([video_path])

        # 等待页面跳转到指定的 URL
        while True:
            # 判断是是否进入视频发布页面，没进入，则自动等待到超时
            try:
                await page.wait_for_url(
                    "https://creator.douyin.com/creator-micro/content/publish?enter_from=publish_page")
                break
            except:
                print("  [-] 正在等待进入视频发布页面...")
                await asyncio.sleep(0.1)

        print("  [-] 正在填充标题和话题...")

        title_blank = page.locator('xpath=//*[@id="root"]/div/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div/div/input')
        await title_blank.click()
        await title_blank.fill(video_name)


        description_blank = page.locator(".notranslate")
        await description_blank.click()
        await page.keyboard.type(description)
        await page.keyboard.press("Enter")
        css_selector = ".zone-container"

        if len(tags) > 5:
            tags = tags[0:5]
            for index, tag in enumerate(tags, 5):
                print("正在添加话题")
                await page.type(css_selector, "#" + tag)
                await page.press(css_selector, "Space")
        else:
            for index, tag in enumerate(tags, start=1):
                print("正在添加话题")
                await page.type(css_selector, "#" + tag)
                await page.press(css_selector, "Space")

        while True:
            # 判断重新上传按钮是否存在，如果不存在，代表视频正在上传，则等待
            try:
                #  新版：定位重新上传
                number = await page.locator('div label+div:has-text("重新上传")').count()
                if number > 0:
                    print("  [-]视频上传完毕")
                    break
                else:
                    print("  [-] 正在上传视频中...")
                    await asyncio.sleep(2)

                    if await page.locator('div.progress-div > div:has-text("上传失败")').count():
                        print("  [-] 发现上传出错了...")

            except:
                print("  [-] 正在上传视频中...")
                await asyncio.sleep(2)

        # 更换可见元素
        # await page.locator('div.semi-select span:has-text("输入地理位置")').click()
        # await asyncio.sleep(1)
        # print("clear existing location")
        # await page.keyboard.press("Backspace")
        # await page.keyboard.press("Control+KeyA")
        # await page.keyboard.press("Delete")
        # await page.keyboard.type("柳州")
        # await asyncio.sleep(1)
        # await page.locator('div[role="listbox"] [role="option"]').first.click()

        # input("按 Enter 键继续...")  # 暂停并等待用户输入
        #
        # # 頭條/西瓜
        third_part_element = '[class^="info"] > [class^="first-part"] div div.semi-switch'
        # 定位是否有第三方平台
        if await page.locator(third_part_element).count():
            # 检测是否是已选中状态 not in 则打开同步，in则关闭
            if 'semi-switch-checked' not in await page.eval_on_selector(third_part_element, 'div => div.className'):
                await page.locator(third_part_element).locator('input.semi-switch-native-control').click()
        #
        #
        # 判断视频是否发布成功
        while True:
            # 判断视频是否发布成功
            try:
                publish_button = page.get_by_role('button', name="发布", exact=True)
                if await publish_button.count():
                    await publish_button.click()
                await page.wait_for_url("https://creator.douyin.com/creator-micro/content/manage",
                                        timeout=1500)  # 如果自动跳转到作品页面，则代表发布成功
                print("  [-]视频发布成功")
                break
            except:
                print("  [-] 视频正在发布中...")
                await page.screenshot(full_page=True)
                await asyncio.sleep(0.5)

        await asyncio.sleep(2)  # 这里延迟是为了方便眼睛直观的观看
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()



