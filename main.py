import re
import os 
import shutil
from datetime import date
from random import randrange
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup 
from PIL import Image
import unicodedata


def sanitize_filename(value):
    # Normalize the string to remove any accents or special characters
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Replace spaces with underscores and remove any non-alphanumeric characters
    value = ''.join(e for e in value if e.isalnum() or e == ' ').replace(' ', '_')
    return value

def fetch_career_elements(soup, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    # get the careers section
    soup = soup.find("div", {"class" ,"AchievementRolesCardsStyled-sc-1yyq2fl-0 kjysNg"})
    career_cards = soup.find_all("li")
    achievements = []
    for card in career_cards:
        title = card.find('h3').text
        url = card.find('a')['href']
        img_src = card.find('img')['src']
        
        # Construct the destination path using the title (ensure it's safe for filenames)
        safe_title = sanitize_filename(title)
        dest_image = os.path.join(dest_dir, f"{safe_title}.webp")  # Convert to WebP

        # Convert the PNG image to WebP and move it
        try:
            with Image.open(img_src) as img:
                # Convert and save the image in WebP format
                img.save(dest_image, 'webp')
                print(f"Converted and moved: {img_src} -> {dest_image}")
        except FileNotFoundError:
            print(f"Image file not found: {img_src}")
        except Exception as e:
            print(f"Error processing file {img_src}: {str(e)}")
        achievement_data = {
            'title': title,
            'url': url,
            'image_src': dest_image.replace('\\', '/')
        }
        achievements.append(achievement_data)
    return achievements

def fetch_badge_elements(soup, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    # Get the badge sections
    sections = soup.find_all("li", {"class": "AchievementsSeriesCategoryStyled-tzope2-0 VlhzS"})
    # Initialize the dictionary to store achievements
    achievements = {}
    # Loop through each section
    for section in sections:
        # Get the section title (inside <h3>)
        section_title = section.find('h3').text.split('(')[0].strip()
        # Initialize a list to store the achievements for this section
        achievements[section_title] = []
        # Find all achievement cards within the section
        cards = section.find_all('div', {'role': 'listitem'})
        # Loop through each card
        for card in cards:
            # Extract the title (inside <h4>)
            title = card.find('h4').text
            # Extract the URL (inside <a>)
            url = card.find('a')['href']
            # Extract the image source (inside <img>)
            img_src = card.find('img')['src']
            # Store the extracted data in a dictionary
                
            # Construct the destination path using the title (ensure it's safe for filenames)
            safe_title = sanitize_filename(title)
            dest_image = os.path.join(dest_dir, f"{safe_title}.webp")  # Convert to WebP
            
            # Convert the PNG image to WebP and move it
            try:
                with Image.open(img_src) as img:
                    # Convert and save the image in WebP format
                    img.save(dest_image, 'webp')
                    print(f"Converted and moved: {img_src} -> {dest_image}")
            except FileNotFoundError:
                print(f"Image file not found: {img_src}")
            except Exception as e:
                print(f"Error processing file {img_src}: {str(e)}")
            achievement_data = {
                'title': title,
                'url': url,
                'image_src': dest_image.replace('\\', '/')
            }
            # Append the dictionary to the achievements list for the current section
            achievements[section_title].append(achievement_data)

    return achievements

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

title: 'Security Studies'
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

    with open(f"index.md", "w") as file:
        file.write(f""" {PAGE_STYLE} \n <ul id="program_list"> \n       <li id="program_item"> """)
        for element in career_elements:
            widget = f""" {{{{< badge url="{element.get('image_src')}" link="{element['url']}" alt="{element['title']}" height="240" >}}}} """
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
                    widget = f""" {{{{< badge url="{element['image_src']}" link="{element['url']}" alt="{element['title']}" height="155" >}}}} """
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
    all_the_soup = BeautifulSoup(contents, 'html.parser',  from_encoding='utf-8') 

    # Define source and destination directories
    dest_dir = './badge_images'

    career_badges = fetch_career_elements(all_the_soup, dest_dir)

    small_badges = fetch_badge_elements(all_the_soup, dest_dir)

    generate_markdown(career_badges , small_badges)


if __name__ == "__main__":
    main()