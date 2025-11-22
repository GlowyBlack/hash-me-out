# import requests
# # https://requests.readthedocs.io/en/latest/user/quickstart/#make-a-request

# defult_image = "https://thumbs.dreamstime.com/b/no-photo-thumbnail-graphic-element-no-found-available-image-gallery-album-flat-picture-placeholder-symbol-vector-no-317104797.jpg"


# def is_url_image(url: str) -> str:
#     if not url:
#         return defult_image
#     # Try to access link and if no response within 5 seconds then close request
#     # to prevent indefinite wait and return default image
#     # allow redirect: If link points to another page, then go try to grab the resource from said redirect
#     try:
#         response = requests.head(url, timeout=5, allow_redirects= True)
#         if response.headers['Content-Type'].lower().startswith("images/") and response.status_code == 200:
#             return url
#     except requests.RequestException:
#         pass
    
#     return defult_image
        
    


