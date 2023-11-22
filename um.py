from flask import Flask, render_template_string, request
from selenium import webdriver
from selenium.webdriver.common.by import By



def get_element_css(driver, element):
    # 요소의 CSS 속성을 추출하는 함수
    properties = driver.execute_script(
        'var items = {};'
        'var computedStyle = getComputedStyle(arguments[0]);'
        'for (var i = 0; i < computedStyle.length; i++) {'
        '   items[computedStyle[i]] = computedStyle.getPropertyValue(computedStyle[i]);'
        '}'
        'return items;', element)
    return '; '.join([f'{k}: {v}' for k, v in properties.items()])

app = Flask(__name__)

def get_element_css(driver, element):
    # 요소의 CSS 속성을 추출하는 함수
    properties = driver.execute_script(
        'var items = {};'
        'var computedStyle = getComputedStyle(arguments[0]);'
        'for (var i = 0; i < computedStyle.length; i++) {'
        '   items[computedStyle[i]] = computedStyle.getPropertyValue(computedStyle[i]);'
        '}'
        'return items;', element)
    return '; '.join([f'{k}: {v}' for k, v in properties.items()])

def crawl_and_get_tables(id, pw):
    webdriver_options = webdriver.ChromeOptions()
    # ... 웹드라이버 옵션 설정 ...
    driver = webdriver.Chrome(options=webdriver_options)
    driver.implicitly_wait(1)

    # 로그인 및 탐색
    login_url = 'https://account.everytime.kr/login'
    driver.get(login_url)
    driver.find_element(By.NAME, 'id').send_keys(id)
    driver.find_element(By.NAME, 'password').send_keys(pw)
    driver.find_element(By.XPATH, '//input[@value="에브리타임 로그인"]').click()

    driver.implicitly_wait(10)
    driver.get('https://everytime.kr/')
    driver.get_screenshot_as_file('capture1.png')

    timetable_url = 'https://everytime.kr/timetable'
    driver.get(timetable_url)
    driver.implicitly_wait(5)
    driver.get_screenshot_as_file('capture2.png')
    table_elements = driver.find_elements(By.TAG_NAME, 'table')

    styled_table_html_list = []
    for table in table_elements:
        style = get_element_css(driver, table)
        styled_table_html = f'<table style="{style}">{table.get_attribute("innerHTML")}</table>'
        styled_table_html_list.append(styled_table_html)

    driver.quit()

    return styled_table_html_list

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # If the form is submitted, get the ID and password from the form
        id = request.form['id']
        pw = request.form['password']
        
        # Get the HTML codes of tables using the provided ID and password
        table_html_list = crawl_and_get_tables(id, pw)
    else:
        # If it's a GET request, initialize the HTML list with an empty list
        table_html_list = []

    all_tables_html = "\n".join(table_html_list)  # 하나의 문자열로 연결

    # HTML template to display the tables
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crawled Tables</title>
    </head>
    <body>
        <form method="post" action="/">
            <label for="id">ID:</label>
            <input type="text" id="id" name="id" required>
            <br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <br>
            <input type="submit" value="Submit">
        </form>
        <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
        {{ tables_html|safe }}
    </body> 
    </html>
    """

    return render_template_string(html_template, tables_html=all_tables_html)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
