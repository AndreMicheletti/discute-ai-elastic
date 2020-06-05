from bs4 import BeautifulSoup
import requests
import unicodedata

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

detailers = [
    {
        # JUDICIÁRIO
        "match": [
            "supremo tribunal federal",
        ],
        "set": {
            "tags": ["estrutura", "judiciario", "brasil"],
            "image_url": "https://discute-ai-images.s3.amazonaws.com/judiciario.jpg"
        }
    },
    {
        # LEGISLATIVO
        "match": [
            "vereador",
            "bancadas parlamentares na câmara dos deputados",
            "blocos partidários na câmara dos deputados",
            "câmara de vereadores",
            "conselho de ética da câmara dos deputados",
            "mesa diretora da câmara dos deputados",
            "presidente da câmara dos deputados",
            "deputado estadual",
            "deputado federal",
            "assembleia legislativa no estado",
            "assembleia constituinte",
            "chefia de gabinete de senador",
            "líder do governo no senado federal",
            "líder partidário no senado",
            "mesa diretora do senado",
            "senado",
            "senador",
            "sessões parlamentares do senado",
            "suplente de senador"
        ],
        "set": {
            "tags": ["estrutura", "legislativo", "brasil"],
            "image_url": "https://discute-ai-images.s3.amazonaws.com/legislativo.jpg"
        }
    },
    {
        # MINISTERIOS
        "match": [
            "ministério da casa civil",
            "ministério da cultura",
            "ministério do desenvolvimento, indústria e comércio exterior",
            "ministério da educação",
            "ministério da fazenda",
            "ministério da justiça",
            "ministério do planejamento, orçamento e gestão",
            "ministério da saúde",
            "ministério público eleitoral",
        ],
        "set": {
            "tags": ["executivo", "brasil", "ministerio"],
            "image_url": "https://discute-ai-images.s3.amazonaws.com/ministerio.png"
        }
    },
    {
        # EXECUTIVO
        "match": [
            "presidente da república",
            "governador",
            "prefeito",
        ],
        "set": {
            "tags": ["estrutura", "executivo", "brasil"],
            "image_url": "https://discute-ai-images.s3.amazonaws.com/executivo.png"
        }
    },
    { "match": ["comunismo", "socialismo", "socialismo utópico", "marxismo"], "set": {
       "tags": ["mundo", "sistema-politico", "comunismo", "socialismo"], "image_url": "https://discute-ai-images.s3.amazonaws.com/comunismo.jpg"
    }},
    { "match": ["fascismo", "nazismo", "neonazismo"], "set": {
       "tags": ["mundo", "sistema-politico", "fascismo"], "image_url": "https://discute-ai-images.s3.amazonaws.com/fascismo.jpg"
    }},
    {
        # IDEOLOGIAS
        "match": [
            "absolutismo",
            "anarquismo",
            "bolchevismo",
            "coletivismo",
            "clientelismo",
            "colonialismo",
            "conservadorismo",
            "coronelismo",
            "individualismo",
            "liberalismo",
            "libertarianismo",
            "nacionalismo",
            "neoliberalismo",
            "patrimonialismo",
            "populismo",
            "progressismo",
            "ufanismo",
        ],
        "set": {
            "tags": ["mundo", "ideologia"],
            "image_url": "https://discute-ai-images.s3.amazonaws.com/socrates.jpg"
        }
    },
    {
        # SISTEMAS POLITICOS
        "match": [
            "democracia",
            "democracia líquida",
            "totalitarismo",
            "república",
        ],
        "set": {
            "tags": ["mundo", "sistema-politico", "regime"],
            "image_url": "https://discute-ai-images.s3.amazonaws.com/democracia.jpg"
        }
    }
    # {
    #     # opa
    #     "match": [
    #
    #     ],
    #     "set": {
    #     }
    # },
]

ADDITIONAL_INFO_TABLE = {}

for detail_query in detailers:
    names = detail_query["match"]
    value = detail_query["set"]

    for name in names:
        ADDITIONAL_INFO_TABLE[name] = value


def save_post_with_details(collection, post: dict, source_id: str):

    doc_values = {
        "title": post["title"],
        "imageUrl": "",
        "tags": ["politize", "politica"],
        "text": post["content"],
        "likes": 0,
        "dislikes": 0,
        "faq": [],
        "references": [],
        "source": source_id,
        "color": "lightblue",
    }

    title_lower = post["title"].lower().strip()

    if title_lower in ADDITIONAL_INFO_TABLE.keys():
        add = ADDITIONAL_INFO_TABLE[title_lower]
        doc_values["tags"].extend(add["tags"])
        doc_values["imageUrl"] = add["image_url"]
        print(f"FOUND MORE INFORMATION FOR {title_lower}")

    doc = collection.document()
    doc.set(doc_values)


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
            save_post_with_details(definitions, post, politize_doc.id)
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
        md = to_markdown(convertible_element)
        if tag.name == "li":
            md = f" - {md}\n"
        result += md
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
