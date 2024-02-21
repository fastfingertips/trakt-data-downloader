from bs4 import BeautifulSoup
import requests

# Class to represent an HTTP response and parse response data
class Responser:

  # Default timeout and parsers
  timeout = 30  
  parser = 'html.parser'
  decode = 'utf-8'

  # Initialize instance with URL 
  def __init__(self, url):
    self.url = url  
    self.response = self.get_response()
    self.dom = self.get_dom()
    self.code = self.get_response_code()
    self.is_success = self.code == 200

  # Make GET request to URL  
  def get_response(self) -> requests.Response:  
    return requests.get(self.url, timeout=self.timeout)

  # Get response status code
  def get_response_code(self) -> int:
    return self.response.status_code

  # Parse response content into DOM  
  def get_dom(self) -> BeautifulSoup:
    """
    Retrieves and parses the DOM from the response content.
    Handles connection and timeout errors.
    """
    # Try/except blocks to catch request errors
    try:
        while True:
            #> https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                dom = BeautifulSoup(self.response.content.decode(self.decode), self.parser)
                if dom: return dom # Returns the page DOM
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
            except KeyboardInterrupt: print("Someone closed the program")
            except Exception as e: print('Error:', e)
    except Exception as e: print('Error:', e)

# Class to represent HTML elements and extract their attributes
class Element:

  # Initialize Element instance and extract name  
  def __init__(self, item: BeautifulSoup, element_name: str):
    self.item = item
    self.name = element_name  
    self.attrs = self.get_attrs()

  def get_attrs(self) -> dict:
    """
    Returns a dictionary of attributes for the given element name.
    
    Searches the provided BeautifulSoup item for all tags matching 
    the element name. Attributes are extracted from each tag and 
    stored in a dictionary keyed by tag name and attribute name.
    """

    element_attrs = {}

    # Find all tags matching the element name
    tags = self.item.find_all(self.name)  

    for tag in tags:
      tag_name = tag.name
      tag_attrs = tag.attrs

      # Extract each attribute
      for tag_att in tag_attrs:  
        content = tag_attrs[tag_att]

        # Add attribute to dictionary
        element_attrs[tag_name+"-"+tag_att] = content

    return element_attrs

# Meta class for extracting metadata attributes from HTML <meta> tags
class Meta:

  # Initialize Meta instance and extract attributes from BeautifulSoup item
  def __init__(self, item:BeautifulSoup):  
    self.item = item
    self.attrs = self.get_attrs()

  def get_attrs(self):
    """
    Returns a dictionary of meta attributes parsed from HTML <meta> tags.
    
    The attributes are extracted from each <meta> tag's name, type 
    and content. Duplicate attributes are consolidated with episode 
    qualifiers.
    """
    
    # Dictionary to store extracted meta attributes
    meta_attrs = {}  

    # Find all <meta> tags in HTML item
    tags = self.item.find_all('meta')  

    for tag in tags:
      # Get tag name and all attributes  
      tag_name = tag.name
      tag_attrs = tag.attrs

      for tag_att in tag_attrs:
        # Extract type from attributes
        meta_type = tag_attrs[tag_att] 

        # Extract content, skipping the tag itself 
        meta_content = tag_attrs['content'] if tag_att != 'content' else None

        # Construct attribute key  
        key = f"{tag_name}-{tag_attrs[tag_att].lower()}"

        # Check for duplicate, qualify with episode
        if key in meta_attrs:
          key = f"{tag_name}-episode-{meta_type.lower()}"

        # Add attribute 
        meta_attrs[key] = meta_content

    return meta_attrs
