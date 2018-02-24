#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 15:32:09 2017

@author: emilyfong
"""

#import important libraries 
import urllib.request as req
import requests
import hashlib
import time


class HeadRequest(req.Request):
    """
    Creates a HeadRequest object that returns the header.
    
    params: A urllib.request object. 
    """
    def get_method(self):
        return "HEAD"
    
    
def downloadFile(url, file_name):
    """
    Downloads a file.
    
    params: URL of the file, name of the file to write to. 
    """
    
    #open connection, stream=True only downloads response headers and keeps
    #connection open without downloading the file immediately
    r = requests.get(url, stream=True)
    with open(file_name, 'wb') as file:
        
        #download for is slow maybe because the chunks are too small?
        for chunk in r.iter_content(1024):
            if chunk:
                file.write(chunk)
    r.close()
    
    
def contentSize(head_info, url):
    """
    Returns the size of a file by reading the "Content-Length" header.
    
    params: Headers, URL of the file. 
    """
    
    #read amount of bytes in the file and convert it to an int from a string
    if "Content-Length" in head_info:
        byte_size = requests.head(url, headers={"Accept-Encoding":"identity"}).headers.get("Content-Length", None)
        return int(byte_size)
    else: 
        print("File size cannot be determined.")
        
        
def checkIntegrity(head_info, url, byte_size, file_name):
    """
    Calculates an MD5 checksum and compares the result stored in the "ETag" header.
    
    params: Headers, URL of the file, size of the file, name of the saved file. 
    """
    
    #get the code from the headers 
    code = requests.head(url, headers={"Accept-Encoding":"identity"}).headers.get("ETag", None)
    
    #hashlib object that reads the contents of the file and generates a hash code
    hasher = hashlib.md5()
    with open(file_name, 'rb') as afile:
        buf = afile.read(byte_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(byte_size)
    
    #format hash code and validate with MD5
    hashed_code = '"' + hasher.hexdigest() + '"'
    if hashed_code == code:
        print("File integrity validated.")
    else:
        print("File integrity validation failed.")
        
        
def main():
    """
    Main program - performs initial check for the "Accept-Ranges" header and formats
    user-friendly output in order to download the file.
    """
    
    #provide source URL
    url = "https://static.pexels.com/photos/414171/pexels-photo-414171.jpeg"
    
    #open connection, get headers, close connection
    response = req.urlopen(HeadRequest(url))
    head_content = response.headers
    response.close()
    
    
    #check for "Accept-Ranges" to determine if server accepts multiple chunks
    if "Accept-Ranges" in head_content:
        
        #start download, read size of file & start timer
        begin_time = time.time()
        print("File downloading...")
        size = contentSize(head_content, url)
        print("Bytes to download: ", size)
        
        #create name for the downloaded file
        saved_file_name = url.split('/')[-1]
        
        #download & print out progress info
        downloadFile(url, saved_file_name)
        end_time = str(time.time() - begin_time)
        print("Download time: " + end_time + "seconds")

        #generate checksum
        print("Finished download. Checking integrity...")
        checkIntegrity(head_content, url, size, saved_file_name)
        
    else: 
        #download file in one chunk & start timer
        begin_time = time.time()
        print("File downloading...")
        size = contentSize(head_content, url)
        print("Bytes to download: ", size)
        
        #create name for the downloaded file
        saved_file_name = url.split('/')[-1]
        
        #download & print progress info
        req.urlretrieve(url, saved_file_name)
        print("Finished download.")
        end_time = str(time.time() - begin_time)
        print("Download time: " + end_time + "seconds")
        
        #generate checksuma
        print("Finished download. Checking integrity...")
        checkIntegrity(head_content, url, size, saved_file_name)
            

going = True

#set up retries in case of error
while going:
    
    #try-catch
    try:
        main()
        going = False
    except Exception as e:
        print(e)
        
        #get user input to retry
        answer = input("An error occured. Would you like to try downloading again? (Type 'y' or 'n'): ")
        if answer == "n":
            print("Download stopped.")
            going = False
        elif answer == "y":
            main()
            going = False
        else:
            print("Invalid input.")
            going = False
        
        
        
        
        
        
        
        
        
