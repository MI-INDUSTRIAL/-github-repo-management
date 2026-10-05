import argparse 
from common import load_request, repo_name 
 
parser = argparse.ArgumentParser() 
parser.add_argument("request_file") 
args = parser.parse_args() 
 
data = load_request(args.request_file) 
name = repo_name(data) 
expected_file = f"requests/{name}.yml" 
actual_file = args.request_file.replace("\\", "/") 
 
if actual_file != expected_file: 
    raise ValueError( 
        f"Request filename must match generated repository name: {expected_file}" 
    ) 
 
print(f"VALID: {actual_file}") 
print(f"Repository: {name}") 
print(f"Visibility: {data['visibility']}")
