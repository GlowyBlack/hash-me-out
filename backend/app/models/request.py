from datetime import datetime
import os
import csv

class Request:
    def __init__(self, requestID: int, bookTitle: str, author: str, isbn: str):
        self.__requestID = requestID
        self.__bookTitle = bookTitle
        self.__author = author
        self.__isbn = isbn
        now = datetime.now()
        self.__timeStamp = now.strftime("%Y-%m-%d")
        
        
    def file_has_header(self, filename):
        if not os.path.exists(filename):
            return False
        with open(filename, encoding='utf-8') as file:
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(file.read(2048))
            file.seek(0)
            
            return has_header

    # from https://stackoverflow.com/questions/40193388/how-to-check-if-a-csv-has-a-header-using-python

        
    # Increments number of times a ISBN has been request and is stored inside file
    def __update_request_total(self):
        pass
        
    
    def __log_request(self):
        has_header = self.file_has_header("backend/app/data/Request_Log.csv")
        with open('./data/Request_Log.csv', 'a', newline = 'a') as csvfile:
            fieldnames = ['RequestID', 'Book Title', 'Author', 'ISBN', 'Time', 'Number of Request']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not has_header:
                writer.writeheader()
            writer.writerow({
                'RequestID': self.__requestID,
                'Book Title': self.__bookTitle,
                'Author': self.__author,
                'ISBN': self.__isbn,
                'Time': self.__timeStamp,
            })
            
                
    def submit_request(self):
        self.__update_request_total()
        self.__log_request()
        
        # all_requests = []
        # with open('', 'r', newline='') as csvfile:
        #     reader = csv.DictReader(csvfile)
        #     for row in reader:
        #         all_requests.append(row)
        
        # # Checking if requested book ISBN already exist and if it does increment number of requests by 1
        # found = False
        # for row in all_requests:
        #     if row['ISBN'] == self.__isbn:
        #         row['Number of Request'] = str(int(row['Number of Request']) + 1)
        #         found = True
        #         break
            
        # if not found:
        #     with open('', 'a', newline = 'a') as csvfile:
        #         fieldnames = ['RequestID', 'Book Title', 'Author', 'ISBN', 'Time', 'Number of Request']
        #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
        #         csvfile.seek(0, 2)
        #         if csvfile.tell() == 0:
        #             writer.writeheader()
                    
        #         writer.writerow({
        #             'RequestID': self.__requestID,
        #             'Book Title': self.__bookTitle,
        #             'Author': self.__author,
        #             'ISBN': self.__isbn,
        #             'Time': self.__timeStamp,
        #             'Number of Request': 1
                    
        #     })
    
    
                
                
        

    

request = Request(1,"Lore", "Test", "1")
request.submit_request()
# if os.path.isfile("C:/Users/aolud/OneDrive/Documents/University/COSC 310/hash-me-out/backend/app/data/Request_Log.csv"):
# if os.path.isfile("backend/app/data/Request_Log.csv"):
#     print("Log file found!")
# else:
#     print("Log file is missing.")
