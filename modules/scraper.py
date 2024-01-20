from bs4 import BeautifulSoup
import requests

def get_dom(_url) -> BeautifulSoup:
    """
    Reads and retrieves the DOM of the specified page URL.
    """
    try:
        while True:
            #> https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                url_response_code = requests.get(_url, timeout=30)
                url_dom = BeautifulSoup(url_response_code.content.decode('utf-8'), 'html.parser')
                if url_dom is not None:
                    return url_dom # Returns the page DOM
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to the Internet. Technical details are provided below.")
                print(str(e))
                continue
            except requests.Timeout as e:
                print("OOPS!! Timeout Error")
                print(str(e))
                continue
            except requests.RequestException as e:
                print("OOPS!! General Error")
                print(str(e))
                continue
            except KeyboardInterrupt:
                print("Someone closed the program")
            except Exception as e:
                print('Error:', e)
    except Exception as e:
        print('Error:', e)

def get_meta_attrs(item) -> dict:
    meta_attrs = {}
    item_meta_tags = item.find_all('meta')
    for meta in item_meta_tags:
        tag_name = meta.name
        tag_attrs = meta.attrs
        for tag_att in tag_attrs:
            meta_type = tag_attrs[tag_att]
            meta_content = tag_attrs['content']

            if tag_att == 'content':
                continue

            # itemprop
            key = f'{tag_name}-{tag_attrs[tag_att].lower()}'
            if key in meta_attrs:
                meta_attrs[f'{tag_name}-episode-{meta_type.lower()}'] = meta_content
            else:
                meta_attrs[key] = meta_content

    return meta_attrs

def get_element_attrs(item:BeautifulSoup, element_name:str) -> dict:
    """
    Returns a dictionary of element attributes.
    """
    element_attrs = {}
    tags = item.find_all(element_name)
    for tag in tags:
        tag_name = tag.name
        tag_attrs = tag.attrs
        for tag_att in tag_attrs:
            content = tag_attrs[tag_att]
            element_attrs[tag_name+'-'+tag_att] = content

    return element_attrs