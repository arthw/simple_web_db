# Simple Web Databbase
This a single code file software to provide RESTFul API and GUI to access the memory key/value Database.

Startup:
 - listen on 8002  
python3 swebdb.py

- listen on 80  
python3 swebdb.py 80

Usage:
 - API:  
 POST http:x.x.x.x:8002:/api  
 JSON  
op:[query, save]  
key:string  
value:string  

 - GUI:  
![GUI](gui.png)
