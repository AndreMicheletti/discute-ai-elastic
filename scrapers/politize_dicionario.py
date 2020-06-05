from bs4 import BeautifulSoup
import requests
import unicodedata

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

credential_path = "creds/discute-ai-firebase-adminsdk-3wsyf-82457e075b.json"
cred = credentials.Certificate(credential_path)
app = firebase_admin.initialize_app(cred)
db = firestore.client()
print("CONNECTED TO FIRESTORE")


URL = "https://www.politize.com.br/dicionario-politica/"


def scrape(url=URL):

    r = requests.get(url)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')

    all_toggle_divs = soup.find_all('div', attrs={"class": "single_toggle"})

    all_posts = []

    try:
        for togg_div in all_toggle_divs:
            content = scrape_toggle_div(togg_div)
            all_posts.append(content)
    except KeyboardInterrupt:
        print("STOPPING")
        return

    # FIREBASE
    references = db.collection(u'sources')
    politize_doc = references.document(u'politize!')
    politize_doc.set({
        "name": "Politize!",
        "background": "white",
        "logo": "https://www.politize.com.br/wp-content/uploads/2018/01/header-home-politize.png",
        "url": "https://www.politize.com.br/"
    })

    definitions = db.collection(u'definitions')
    try:
        for post in all_posts:
            print(f"SAVING DOC {post['title']}")
            doc = definitions.document()
            doc.set({
              "title": post["title"],
              "imageUrl": "",
              "tags": ["politize", "politica"],
              "text": post["content"],
              "likes": 0,
              "dislikes": 0,
              "faq": [],
              "references": [],
              "source": politize_doc.id,
              "color": "lightblue",
            })
    except KeyboardInterrupt:
        print("STOPPING")
        return


def scrape_toggle_div(div):

    title = div.find('p').text

    content_div = div.find('div', attrs={'itemprop': 'text'})
    markdown_content = parse_texts_and_links_to_markdown(content_div)

    return {
        "title": title,
        "content": markdown_content
    }


def parse_texts_and_links_to_markdown(parent):

    result_markdown = ""

    for element in parent.children:
        if element.name is None:
            continue
        if element.name in ['ul', 'ol', 'blockquote']:
            for li in element.children:
                result_markdown += discover_and_parse_children(li)
        elif element.name in ['p']:
            result_markdown += discover_and_parse_children(element)
        elif element.name == 'section':
            for div in element.find_all('p'):
                result_markdown += discover_and_parse_children(div)
        else:
            raise NotImplementedError(f"RECURSION FOR TAG {element.name} NOT IMPLEMENTED")
    return result_markdown.replace('\xa0', ' ')


def discover_and_parse_children(tag):
    # all these children must be markdown convertible
    if tag.name is None:
        return ""
    result = ""
    for convertible_element in tag.children:
        result += to_markdown(convertible_element)
    return result


def to_markdown(tag):

    if tag.name is None:
        return unicodedata.normalize("NFC", tag)

    tag_text = unicodedata.normalize("NFC", tag.text)
    if tag.name == 'span':
        return tag_text
    if tag.name in ['b', 'strong']:
        return f"**{tag_text}**"
    if tag.name in ['i', 'em']:
        return f"*{tag_text}*"
    if tag.name == 'a':
        return f"[{tag_text}]({tag.get('href')})"
    raise NotImplementedError(f"CONVERTION FROM TAG <{tag.name}> WAS NOT IMPLEMENTED")


scrape()
