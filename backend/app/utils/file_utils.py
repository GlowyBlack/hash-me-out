# import os
  
# def file_has_header(filename:str, header:str) -> bool:
#     if not os.path.exists(filename):
#         return False
#     with open(filename, 'r', encoding='utf-8') as file:
#         first_line = file.readline().strip()
#         return first_line == header