import os, re
import argparse


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True, help='Directory of input XML files')
    parser.add_argument('--output-dir', required=True, help='Directory to save processed output')
    args = parser.parse_args()

    return args

def processing_xml(path):

    # Processing XML files in case that errors are encounterred when using Pubmed Parser

    with open(path, 'r', encoding='utf-8') as f:
        xml = f.read()

    # remove ref-list, extract all figs, strip them from main body, then append
    xml = re.sub(r'<ref-list.*?</ref-list>', '', xml, flags=re.DOTALL)
    figs = re.findall(r'<fig .*?<caption>.*?</fig>', xml, flags=re.DOTALL)
    xml = re.sub(r'<fig .*?</fig>', '', xml, flags=re.DOTALL)
    xml = xml.replace('</article>', ''.join(figs) + '</article>')

    return xml

def main(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for fn in os.listdir(input_dir):
        if not fn.lower().endswith(('.xml', '.nxml')):
            continue
        in_path = os.path.join(input_dir, fn)
        out_path = os.path.join(output_dir, fn)
        cleaned = processing_xml(in_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)

if __name__ == '__main__':

    args = parse_args()

    main(args.input_dir, args.output_dir)