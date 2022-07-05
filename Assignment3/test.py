from timeit import timeit
import requests
import timeit

url = "http:127.0.0.1:5000"

print(timeit.timeit("requests.post(url,data={'input':28,from:'',to:''})",number=20))