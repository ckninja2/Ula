import asyncio
import urllib.request
from flask import Flask, request
from seleniumbase import SB
from selenium.webdriver.common.by import By

app = Flask(__name__)

# Shared state for terminal output
terminal_output = {"text": ""}


def sel(u, p, s):
    with SB(uc=True, headless=True) as sb:
        try:
            sb.get('https://www.google.com')
            sb.click('#W0wltc')
            sb.send_keys('#APjFqb', 'Shell Cloud Google')
            sb.submit('#APjFqb')
            sb.click('//a[contains(@href, "https://shell.cloud.google.com/")]', by="xpath")
            sb.send_keys('#identifierId', u)
            sb.click('//*[@id="identifierNext"]/div/button', by='xpath')
            sb.send_keys('//*[@id="password"]/div[1]/div/div[1]/input', p, by='xpath')
            sb.click('//*[@id="passwordNext"]/div/button', by='xpath')
            sb.click('strong:contains("Google Authenticator")')
            sb.enter_mfa_code('#totpPin', s)
            button = sb.wait_for_element(
                '//*[@id="cloudshell"]/standalone-header/div/mat-toolbar/span/cloudshell-view-controls/visibility-toggle[1]/button',
                by='xpath',
                timeout=60,
            )
            if button.get_attribute('aria-label') == 'Close Editor':
                button.click()

            terminal_tab = sb.wait_for_element(
                '//*[@id="cloudshell"]/div/horizontal-split/div[2]/devshell/terminal-container/div/xterm-terminal-tab',
                by='xpath',
                timeout=60,
            )
            terminal_input_div = sb.wait_for_element(
                '//*[@id="cloudshell"]/div/horizontal-split/div[2]/devshell/terminal-container/div/xterm-terminal-tab/div/xterm-terminal/div/div/div/div[3]/div[1]',
                by='xpath',
                timeout=60,
            )
            terminal_input = terminal_input_div.find_elements(By.CSS_SELECTOR, 'textarea')[0]

            count = 0
            sleep_for = 5
            while True:
                terminal_input.send_keys(f'echo {count * sleep_for} Seconds have passed\n')
                sb.sleep(0.1)
                splitter = f'{u}@cloudshell:~$'
                output = (splitter + terminal_tab.text.split(splitter)[-2])[:-1]
                terminal_output["text"] = output
                print(output)
                count += 1
                sb.sleep(sleep_for)
        finally:
            sb.save_screenshot('screenshot.png')


def get_google_time():
    request = urllib.request.Request("http://www.google.com", method="HEAD")
    with urllib.request.urlopen(request) as response:
        date_str = response.headers["Date"]
    return date_str


@app.route('/start_server')
def start():
    # Ensure credentials are passed (or load dynamically)
    u = request.args.get('username', 'default_user')
    p = request.args.get('password', 'default_pass')
    s = request.args.get('mfa_code', 'default_mfa')

    # Run the Selenium task in a separate thread
    asyncio.create_task(asyncio.to_thread(sel, u, p, s))
    return "Server started!"


@app.route('/')
def hello():
    if terminal_output["text"]:
        return terminal_output["text"].replace("\n", "<br>")
    return "Terminal not ready yet"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
