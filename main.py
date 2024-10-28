import requests
from bs4 import BeautifulSoup
import json

url = "https://www.irctirethailand.com/%e0%b8%9c%e0%b8%a5%e0%b8%b4%e0%b8%95%e0%b8%a0%e0%b8%b1%e0%b8%93%e0%b8%91%e0%b9%8c/"

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

tire_type_list = soup.select(".et_pb_module.et_pb_has_overlay")

# Initialize an empty list to store all tire data
tire_data = []

for tire_type in tire_type_list:
    tire_type_name = tire_type.find_all("img")[0].get("title")
    tire_type_link = tire_type.find_all("a")[0].get("href")

    # Initialize a dictionary to store tire type and its details
    tire_type_data = {
        "tire_type": tire_type_name,
        "tire_link": tire_type_link,
        "tires": [],
    }

    # Get all tires in this type
    tire_response = requests.get(tire_type_link)
    tire_response.raise_for_status()

    tire_soup = BeautifulSoup(tire_response.text, "html.parser")
    tire_list = tire_soup.select("li.product")

    for tire in tire_list:
        tire_link = tire.find_all("a")[0].get("href")

        tire_detail_response = requests.get(tire_link)
        tire_detail_response.raise_for_status()

        tire_detail_soup = BeautifulSoup(tire_detail_response.text, "html.parser")
        tire_detail_name = tire_detail_soup.find_all("h1")[0].text
        tire_detail_description_loop = tire_detail_soup.select(
            ".et_pb_wc_description_0_tb_body"
        )[0].find_all("li")

        tire_detail_description = "\n".join(
            item.text for item in tire_detail_description_loop
        )

        tire_detail_img = tire_detail_soup.find_all("img", class_="wp-post-image")[
            0
        ].get("src")

        # Get tire sizes
        tire_size_table = tire_detail_soup.find_all("table")[0]
        tire_sizes = tire_size_table.find_all("tr")

        # Initialize a list to store sizes for each tire
        sizes = []

        for i, tire_size in enumerate(tire_sizes):
            if i < 2:  # Skip header rows
                continue

            tire_size_detail = tire_size.find_all("td")

            # Check if we have enough columns to avoid index errors
            if len(tire_size_detail) < 7:
                print(f"Skipping incomplete row in {tire_detail_name}")
                continue

            size_info = {
                "wheel_position": tire_size_detail[0].text.strip(),
                "size": tire_size_detail[1].text.strip(),
                "pattern_type": tire_size_detail[2].text.strip(),
                "diameter": tire_size_detail[3].text.strip(),
                "width": tire_size_detail[4].text.strip(),
                "measurement_rim": tire_size_detail[5].text.strip(),
                "standard_rim": tire_size_detail[6].text.strip(),
            }
            sizes.append(size_info)

        # Append tire details to the tire type data
        tire_type_data["tires"].append(
            {
                "name": tire_detail_name,
                "description": tire_detail_description,
                "image": tire_detail_img,
                "sizes": sizes,
            }
        )

    # Add the tire type data to the main list
    tire_data.append(tire_type_data)

# Write data to JSON file
with open("tire_data.json", "w", encoding="utf-8") as f:
    json.dump(tire_data, f, ensure_ascii=False, indent=4)

print("Data saved to tire_data.json")
