from datetime import datetime
import os
import csv

class Request:
    def __init__(self, requestID: int, userID: int, bookTitle: str, author: str, isbn: str):
        self.__request_id = requestID
        self.__user_id = userID
        self.__book_title = bookTitle
        self.__author = author
        self.__isbn = isbn
        now = datetime.now()
        self.__time_stamp = now.strftime("%Y-%m-%d")
        
        
    def file_has_header(self, filename:str, header:str) -> bool:
        if not os.path.exists(filename):
            return False
        with open(filename, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
            return first_line == header

        
    # Increments number of times a ISBN has been request and is stored inside file
    def __update_request_total(self):
        file_path = "backend/app/data/Total_Requested.csv"
        fieldnames = ['ISBN', 'Total Requested']
        expected_header = ",".join(fieldnames)
        has_header = self.file_has_header(file_path, expected_header)
        all_requests = []
        
        # Creating the Total Requsted File if it doesnt exist
        with open(file_path, 'a', newline = '') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not has_header:
                writer.writeheader()
            has_header = True
        
        # Reading all the data in the Total Requested File
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                all_requests.append(row)
                
        # Checking if requested book ISBN already exist and if it does increment number of 
        # requests by 1
        found = False
        for row in all_requests:
            if row['ISBN'] == self.__isbn:
                row['Total Requested'] = str(int(row['Total Requested']) + 1)
                print(row['Total Requested'])
                found = True
                break
            
        # If requested book doesnt already exist inside the file, add it and set count to 1
        if not found:
            all_requests.append({
                'ISBN': self.__isbn,
                'Total Requested': '1'
            })
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_requests)

                
    # Logs book request into the database
    def __log_request(self):
        file_path = "backend/app/data/Request_Log.csv"
        fieldnames = ['RequestID', 'UserID', 'Book Title', 'Author', 'ISBN', 'Time']
        expected_header = ",".join(fieldnames)
        
        has_header = self.file_has_header(file_path,expected_header)
        with open(file_path, 'a', newline = '') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not has_header:
                writer.writeheader()
        
        # Creating a set to make sure that a user can't request same book more than once
        existing_pairs = set() 
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_pairs.add((row['UserID'], row['ISBN']))

        if (str(self.__user_id), str(self.__isbn)) in existing_pairs:
            return 
          
        with open(file_path, 'a', newline = '') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'RequestID': self.__request_id,
                'UserID': self.__user_id,
                'Book Title': self.__book_title,
                'Author': self.__author,
                'ISBN': self.__isbn,
                'Time': self.__time_stamp,
            })
        self.__update_request_total()

            
    def submit_request(self):
        self.__log_request()
        
request = Request(1, 222, "Percy Jackson and the Lightning Thief", "Rick Riordan", "9780307245304")
request.submit_request()
