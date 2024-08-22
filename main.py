from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from random import randrange
from LinkedinScraper import linkedin_login, fetch_user_location, fetch_user_profile_image, check_and_navigate
import helper
import os

app = Flask(__name__)

@app.route('/', endpoint='index')
def index():
    current_page = int(request.args.get('page', 1))
    total_pages = get_total_pages(1)

    item = get_data_single(current_page, 1)

    item = update_row(list(item))

    return render_template('index.html', 
                           item=item, 
                           current_page=current_page,
                           total_pages=total_pages)


@app.route('/random', endpoint='random')
def index():
    total_pages = get_total_pages(1)

    random_page = randrange(1, total_pages)

    return redirect(url_for('index', page=random_page))
    

@app.route('/open/<id>', endpoint='open')
def open(id):
    data = get_row(id)
    check_and_navigate(driver=driver, target_url=data[2])

    return render_template('index.html', 
                           item=data, 
                           current_page=0,
                           total_pages=0)

@app.route('/unfollow/<id>', endpoint='unfollow')
def unfollow(id):
    script = """
function getElementByXPath(xpath) {
return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

let element = getElementByXPath("//div[@role='button' and contains(@aria-label, 'Remove your connection') and contains(.//span, 'Remove Connection')]");
if (element) {
element.click();
return "Element clicked";
} else {
return "Element not found";
}
"""
    driver.execute_script(script)
    
    with sqlite3.connect(helper.getDatabaseFilePath()) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE linkedin_data SET ConnectionStatus = ? WHERE Id = ?', ("Unfollowed", id))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/keep/<id>', endpoint='keep')
def keep(id):
    with sqlite3.connect(helper.getDatabaseFilePath()) as conn:
        cursor = conn.cursor()
        cursor.execute(f'UPDATE linkedin_data SET ConnectionStatus = ? WHERE Id = ?', ('Keep', id))
        conn.commit()
    return redirect(url_for('index'))

def update_row(row):
    id = row[0]
    url = row[2]
    location = ""
    image = ""

    if url == "" or url is None:
        return None  # Skip rows without a valid URL
    
    if row[5] != "" and row[6] != "":
        driver.get(url)
        return row

    try:
        location = fetch_user_location(driver, url)
        image = fetch_user_profile_image(driver, url)

        with sqlite3.connect(helper.getDatabaseFilePath()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE linkedin_data
                SET Location = ?, Image = ?
                WHERE Id = ?
            ''', (location, image, id))
            conn.commit()
            
            row[6] = image
            row[5] = location

            return row
    except Exception as e:
        print(f"Error processing row {row}: {e}")
        return False

def get_data_single(page = 1, limit = 10):
    with sqlite3.connect(helper.getDatabaseFilePath()) as conn:
        cursor = conn.cursor()
        query = (f'SELECT Id, ("FirstName" || " " || "LastName") AS FullName, URL, Company, Position, Location, Image '
                 f'FROM linkedin_data '
                 f'WHERE ConnectionStatus NOT IN ("Keep", "Unfollowed") '
                 f'AND "FullName" != "" '
                 f'AND URL != "" '
                 f'ORDER BY Location, Company, Position, Id '
                 f'LIMIT {limit} OFFSET {page * limit}')
        cursor.execute(query)
        data = cursor.fetchone()

    return data

def get_row(id):
    with sqlite3.connect(helper.getDatabaseFilePath()) as conn:
        cursor = conn.cursor()
        query = (f'SELECT Id, ("FirstName" || " " || "LastName") AS FullName, URL, Company, Position, Location, Image '
                 f'FROM linkedin_data '
                 f'WHERE Id = ?')
        cursor.execute(query, (id,))
        data = cursor.fetchone()

    return data

def read_data(page = 1, limit = 10):
    data = []

    with sqlite3.connect(helper.getDatabaseFilePath()) as conn:
        cursor = conn.cursor()
        query = (f'SELECT Id, ("FirstName" || " " || "LastName") AS FullName, URL, Company, Position, Location, Image '
                 f'FROM linkedin_data '
                 f'WHERE ConnectionStatus NOT IN ("Keep", "Unfollowed") '
                 f'AND "FullName" != "" '
                 f'AND URL != "" '
                 f'ORDER BY Location, Company, Position, Id '
                 f'LIMIT {limit} OFFSET {page * limit}')
        cursor.execute(query)
        data = cursor.fetchall()

    return data

def get_total_pages(limit = 10):
    with sqlite3.connect(helper.getDatabaseFilePath()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM linkedin_data WHERE ConnectionStatus NOT IN ("Keep", "Unfollowed")')
        total = cursor.fetchone()[0]

    return total // limit

if __name__ == "__main__":
    driver = linkedin_login(helper.getUsername(), helper.getPassword())

    app.run(host='0.0.0.0', port=8000)
