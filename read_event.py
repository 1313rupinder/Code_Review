import json 

with open ("sample_event.json") as f:
    event = json.load(f)

print("Action:", event["action"])
print("PR number:", event["number"])
print("Title:", event["pull_request"]["title"])
print("Repo:", event["repository"]["full_name"])
print("Head Commit:", event["pull_request"]["head"]["sha"])