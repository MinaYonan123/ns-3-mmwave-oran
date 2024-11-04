import json
import os

path = "policies/"


def create_policy(item, policy_id):
    with open(path + policy_id + ".json", "w") as outfile:
        json.dump(item.json(), outfile)


def update_policy(policy_id, threshold):
    with open(path + policy_id + ".json", "r") as outfile:
        json_string = json.load(outfile)
        json_object = json.loads(json_string)
        json_object["threshold"] = threshold
    with open(path + policy_id + ".json", "w") as outfile:
        json.dump(json_object, outfile)


def delete_policy(policy_type_id):
    policy_file = path + policy_type_id + ".json"
    if os.path.isfile(policy_file):
        os.remove(policy_file)

