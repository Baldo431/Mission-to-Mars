# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Run scrape functions
    news_title, news_paragraph = mars_news(browser)
    images = featured_image(browser)
    facts = mars_facts()
    hemispheres = mars_hemispheres(browser)

    # Store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": images,
        "facts": facts,
        "hemisphere_images": hemispheres,
        "last_modified": dt.datetime.now()
    }

    # End Splinter session
    browser.quit()

    return data


# Scrape Mars News
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


# ## JPL Space Images Featured Image
def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url
    


# ## Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframef
    df.columns=df.iloc[0]
    df = df[1:]
    df.set_index(['Mars - Earth Comparison', 'Mars', 'Earth'], inplace=True)
    
    return df.to_html(classes='dataframe table-responsive table-striped table-hover')



def mars_hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    # Convert the base url visited to html
    hemisphere_soup = soup(browser.html, 'html.parser')

    #Search for the objects that contain the information for each hemisphere
    try:
        links_soup = hemisphere_soup.find('div', class_='collapsible results')
        links_soup = links_soup.find_all('div', class_='description')
    except AttributeError:
        return None

    #Iterate through the hemispheres
    for item in links_soup:
        
        try:
            #Pull the url where the full image is located.
            url_to_visit = item.find('a', class_='itemLink product-item').get('href')
            #Pull the title for each hemisphere.
            title = item.find('h3').get_text()
        except AttributeError:
            return None

        browser.visit(f'{url}{url_to_visit}')
        
        # Search for the link to the full sized image
        html = browser.html
        image_soup = soup(html, 'html.parser')

        try:
            image_url = image_soup.find('a', string='Sample').get('href')
        except AttributeError:
            return None        

        #Add the info as a dictionary to the list
        hemisphere_image_urls.append({'img_url' : f'{url}{image_url}', 'title': title})

    # 4. Return a list that holds the dictionary of each image url and title.
    return hemisphere_image_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())






