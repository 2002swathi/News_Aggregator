from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from IPython.display import display, HTML, Image
from difflib import SequenceMatcher

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news', methods=['GET', 'POST'])
def news():
    if request.method == 'POST':
        user_choice = request.form['topic']
        topics = {
            '1': 'Thiruvananthapuram',
            '2': 'Kollam',
            '3': 'Pathanamthitta',
            '4': 'Alappuzha',
            '5': 'Kottayam',
            '6': 'Idukki',
            '7': 'Ernakulam',
            '8': 'Thrissur',
            '9': 'Palakkad',
            '10': 'Malappuram',
            '11': 'Kozhikode',
            '12' :'Wayanad',
            '13' :'Kannur',
            '14' :'Kasargod'
        }
        selected_topic = topics.get(user_choice)
        if selected_topic:
            mathrubhumi_titles = mathrubhumi_news(selected_topic)
            manorama_titles = manorama_news(selected_topic)
            similarity_ratio = compare_titles(mathrubhumi_titles, manorama_titles)
            return render_template('news.html', mathrubhumi_titles=mathrubhumi_titles, manorama_titles=manorama_titles,similarity_ratio=similarity_ratio,topic=selected_topic)
        else:
            return "Invalid choice. Please enter a valid number."
    return render_template('news_form.html')

def mathrubhumi_news(topic):
    alternative_spellings = {'kasargod': 'Kasaragod'}
    topic= alternative_spellings.get(topic.lower(), topic)
    url = f"https://newspaper.mathrubhumi.com/{topic.lower()}/news"
    r = requests.get(url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        articles = soup.find_all("div", class_="mpp-section-card mpp-hover")

        if articles:
            news_list = []
            for article in articles:
                news_dict = {}

                # Extract and store news title
                news_title_element = article.find("h1", class_="malayalam")
                news_title = news_title_element.text.strip() if news_title_element else "Title not available"
                news_dict['title'] = news_title

                # Extract and store news content
                news_content_element = article.find("p", class_="malayalam")
                news_content = news_content_element.text.strip() if news_content_element else "Content not available"
                news_dict['content'] = news_content

                # Extract and store article link
                outer_div = article.find("div", class_="mpp-section-card-content mpp-hover d-flex justify-content-between")
                if outer_div:
                    article_link = outer_div.find("a", href=True)
                    if article_link:
                        full_article_link = f"https://newspaper.mathrubhumi.com{article_link['href']}"
                        news_dict['article_link'] = full_article_link

                # Extract and store images
                picture_tag = article.find('picture')
                if picture_tag:
                    source_tags = picture_tag.find_all('source')
                    image_links = []
                    for source_tag in source_tags:
                        source_image_source = source_tag['srcset']
                        source_image_source_absolute = urljoin(url, source_image_source)
                        image_links.append(source_image_source_absolute)
                    news_dict['images'] = source_image_source_absolute
                news_list.append(news_dict)
            return news_list
        else:
            return f"No articles found for {topic.capitalize()}"
    else:
        return f"Failed to retrieve the page. Status code: {r.status_code}"


###############################################################################

def manorama_news(topic):
    url = f"https://www.manoramaonline.com/district-news/{topic.lower()}.html"
    r = requests.get(url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        articles = soup.find_all("div", class_="cmp-story-list__item-in")

        if articles:
            news_list = []
            for article in articles:
                news_dict = {}

                # Extract and store news title
                news_title_element = article.find("h2", class_="cmp-story-list__title")
                news_title = news_title_element.text.strip() if news_title_element else "Title not available"
                news_dict['title'] = news_title
                outer_div = article.find("div", class_="cmp-story-list__content")


                if outer_div:
                    article_link = outer_div.find("a", href=True)
                    if article_link:
                        full_article_link = f"https://www.manoramaonline.com/{article_link['href']}"
                        news_dict['article_link'] = full_article_link

                # Extract and store images
                image_div = article.find('div', class_='cmp-story-list__image-block')
                if image_div:
                    anchor_tag = image_div.find('a', class_='cmp-story-list__image-link')
                    if anchor_tag:
                        img_tag = anchor_tag.find('img', class_='cmp-story-list__img lazyload')
                        if img_tag:
                            image_source_relative = img_tag.get('data-websrc') or img_tag.get('src')
                            if image_source_relative:
                                image_source_absolute = urljoin(url, image_source_relative)
                                news_dict['image'] = image_source_absolute

                news_list.append(news_dict)

            return news_list
        else:
            return f"No articles found for {topic.capitalize()}"
    else:
        return f"Failed to retrieve the page. Status code: {r.status_code}"
##################################################################################

def compare_titles(titles1, titles2):
    max_similarity_ratio = 0
    for title1 in titles1:
        for title2 in titles2:
            similarity_ratio = SequenceMatcher(None, title1['title'], title2['title']).ratio()
            if similarity_ratio > max_similarity_ratio:
                max_similarity_ratio = similarity_ratio
                
    return "{:.2%}".format(max_similarity_ratio)

##################################################################################

if __name__ == '__main__':
    app.run(debug=True)
