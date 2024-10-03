import os
import re

# Processing XML files in case that errors are encounterred when using Pubmed Parser

def main():
    # Directory containing XML files
    base = "BASE/TO/XML_FILES/"
    files = os.listdir(base)
    
    for file_name in files:
        path = os.path.join(base, file_name)
        processing_xml(path)

def processing_xml(path):  # move all the figure captions to the end
    
    with open(path, 'r', encoding='utf-8') as in_file:
        xml_data = in_file.read()

    xml_data = re.sub(r'<ref-list.*?</ref-list>', '', xml_data, flags=re.DOTALL)
    fig_tags = re.findall(r'<fig .*?<caption>.*?</fig>', xml_data, flags=re.DOTALL)
    xml_data = re.sub(r'<fig .*?</fig>', '', xml_data, flags=re.DOTALL)
    xml_data = re.sub(r'</article>', ''.join(fig_tags) + '</article>', xml_data)

    with open(path, 'w', encoding='utf-8') as out_file:
        out_file.write(xml_data)

if __name__ == "__main__":
    main()