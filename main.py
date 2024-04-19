import re
from datetime import date
from random import randrange
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup 



class achievements_bot():
    def __init__(self):
      options = webdriver.ChromeOptions()
    #   options.add_argument('--headless')
      self.driver = webdriver.Chrome(options=options)

    def __get_achievement_page(self, url):
        """ Get achievement page and extract specified elements"""
        try:
            # Sanitise & return url
            share_url = url.replace("gfk.", "api.")
            share_url = share_url.replace("achievement", "achievements")
            self.driver.get(share_url)
            sleep(randrange(6,7))

            # Locate & extract title
            title_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
            title = title_element.text


            # Locate & extract image url
            image_element = self.driver.find_element(By.XPATH, "//img[@data-qaid='image-badge']")
            img_src = image_element.get_attribute("src")
            # urllib.request.urlretrieve(image_element.get_attribute("src"), f"badges/{title}.png")

        except:
            print(f"ERROR ==== {url} or {share_url}")
            try:
                # Clean & return url
                share_url = url.replace("gfk.", "")
                # share_url = share_url.replace("achievement", "achievements")
                self.driver.get(share_url)
                sleep(randrange(5,7))

                # Locate & extract title
                title_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
                title = title_element.text


                # Locate & extract image url
                image_element = self.driver.find_element(By.XPATH, "//img[@data-qaid='image-badge']")
                img_src = image_element.get_attribute("src")
                # urllib.request.urlretrieve(image_element.get_attribute("src"), f"badges/{title}.png")
                # raise Exception(f"Problem with fetching achievement {share_url}")
            except:
                print(f"FATAL ERROR ==== {url} or {share_url}")
                return None
        Formatter = {'title': title, 'share_url': share_url, 'img_url': img_src }
        # print(Formatter)
        return Formatter

    def __sanitise_section_title(self, text):
         # Regular expression pattern to match numbers and parentheses
        pattern = r'\d+|\(|\)'
        
        # Replace matches with an empty string
        cleaned_text = re.sub(pattern, '', text)
        return cleaned_text.strip()

    def fetch_career_elements(self, soup):
        # get the careers section
        soup = soup.find("section", {"class" ,"AchievementRolesSectionStyled-sc-1di1trd-1 eJxUgL"})
        career_elements = soup.find_all("a", {"class", "sc-hTZhsR fRUjTg"})
        careers_arr = []
        for element in career_elements:
            result = self.__get_achievement_page(element.get("href"))
            if result is not None:
                careers_arr.append(result)
            # break
        # print(career_elements)
        return careers_arr # [{share_url, img_url, title}]
    
    def fetch_badge_elements(self, soup):
        # Get the badge sections
        soup = soup.find_all("li", {"class" ,"AchievementsSeriesCategoryStyled-tzope2-0 VlhzS"})
        badge_sections_arr = {}
        for section in soup:
            section_title = self.__sanitise_section_title(section.find("h3").text)
            badge_elements = section.find_all("a", {"class", "sc-hTZhsR fRUjTg"})
            badge_section = []
            for element in badge_elements:
                result = self.__get_achievement_page(element.get("href"))
                if result is not None:
                    badge_section.append(result)
                # break
            badge_sections_arr[section_title] = badge_section
            # break
        return badge_sections_arr
        # career_elements = soup.find_all("a", {"class", "sc-hTZhsR fRUjTg"})
        # careers_arr = []
        # for element in career_elements:
        #     careers_arr.append(self.__get_achievement_page(element.get("href")))
        #     break
        # return badge_elements # {Section_title: [{share_url, img_url, title}]}

def generate_html(career_elements, badge_elements):
    career_content = "\n".join(f'<a href="{element['share_url']}" target="_blank" rel="noopener"> <img src={element['img_url']} alt="{element['title']}"/></a>' for element in career_elements)
    
    sub_badges = ""
    for key, badges in badge_elements.items():
        sub_badges += f"<h5>{key}</h5>\n"
        sub_badges += "\n".join(f'<a href="{element['share_url']}" target="_blank" rel="noopener"> <img src={element['img_url']} alt="{element['title']}" /></a>' for element in badges)
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Certifications</title>
        <style>
            .careers_badge {{
                /* CSS styles for class 1 */
            }}
            
            .sub_badge {{
                /* CSS styles for class 2 */
            }}
        </style>
    </head>
    <body>
        <h1>Certifications</h1>
        <div class="careers_badge">
            {career_content}
        </div>
        <div class="sub_badge">
            {sub_badges}
        </div>
    </body>
    </html>
    """

    filename = "certs.html"
    with open(filename, "w") as f:
        f.write(html_template)
    print(f"HTML page generated: {filename}")   

def generate_markdown(career_elements, badge_elements):
    # Height = 240
    # Height = 180 

    PAGE_STYLE = f"""
---
draft: false

title: ''
date: '{date.today()}'

cover:
    image: immersive_labs_logo.webp
    alt: "EpicImmersiveLabs.webp"

ShowReadingTime: false
---

<style>
    #program_list {{
        width: 800px;
    }}

    #program_item {{
        width: 100%;
        overflow: hidden;
        float: none;
        padding: 10px 0;
        border-bottom: 1px solid #666;
    }}
</style>

This page is generated from a custom script I wrote. The script scrapes my immersive labs achievements page and rebuilds it for my personal website. If you are interested checkout my [post](https://williamsmale.com/thoughts/tech/coding-convenience-immersive-labs-achievements-scraper/) on it! \n

    """

    with open(f"output.md", "w") as file:
        file.write(f""" {PAGE_STYLE} \n <ul id="program_list"> \n       <li id="program_item"> """)
        for element in career_elements:
            widget = f""" {{{{< badge url="{element.get('img_url')}" link="{element['share_url']}" alt="{element['title']}" height="240" >}}}} """
            file.write('\n')
            file.write(widget)
        
        file.write('\n  </li> ')

        # ============================================
        # === Need to edit when new category added ===
        # ============================================
        print_order = ["Cloud Security", "Offensive Cyber", "Defensive Cyber", "Application Security", "Fundamentals"]
        try:
            for key in print_order:
                print(f"Writing {key}")
                file.write(f'\n <li id="program_item"> \n')
                file.write(f'\n ### {key} \n')
                for element in badge_elements[key]:
                    widget = f""" {{{{< badge url="{element['img_url']}" link="{element['share_url']}" alt="{element['title']}" height="180" >}}}} """
                    file.write('\n')
                    file.write(widget)
                file.write(f' \n </li>')
            file.write(f' \n </ul>')
        except:
            print(badge_elements)

# Opening the local html file 
def main():
    achievements_file = "Achievements - Immersive Labs.html"
    HTMLFile = open(achievements_file, "r") 
    contents = HTMLFile.read() 
    all_the_soup = BeautifulSoup(contents, 'html.parser') 
    bot = achievements_bot()
    career_badges = bot.fetch_career_elements(all_the_soup)
    small_badges = bot.fetch_badge_elements(all_the_soup)

    generate_markdown(career_badges , small_badges)


if __name__ == "__main__":
    main()