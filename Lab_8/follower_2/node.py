import uuid
import requests


class RESTNode:

    def __init__(self, leader : bool, followers : list =None):
        self.users = {}
        self.leader = leader

        if self.leader:
            self.followers = followers


    def create(self, user_dict : dict):
        if self.leader:
            index = str(uuid.uuid4())
            user_dict["id"] = index

        if user_dict["id"] not in self.users:
            self.users[user_dict["id"]] = user_dict

            if self.leader:
                for follower in self.followers:
                    requests.post(f"http://{follower['host']}:{follower['port']}/user",
                                  json = user_dict,
                                  headers = {"Token" : "Leader"})
            return user_dict, 200
        else:
            return {
                "message" : "Error: User already exists!"
            }, 400


    def get_user(self, index : str):
        if index in self.users:
            return self.users[index], 200
        else:
            return {
                "message" : "Missing user!"
            }, 404


    def get_users(self, user_id_list : list):
        missing_ids = set(user_id_list).difference(list(self.users.keys()))

        if len(missing_ids) > 0:
            return {
                "message" : "Missing ids!",
                "ids" : list(missing_ids)
            }, 404
        else:
            user_info = {index : self.users[index] for index in user_id_list}
            return user_info, 200


    def update_user(self, index : str, user_dict : dict):
        if index in self.users:
            self.users[index].update(user_dict)

            if self.leader:
                for follower in self.followers:
                    requests.put(f"http://{follower['host']}:{follower['port']}/user/{index}",
                                 json = self.users[index],
                                 headers = {"Token" : "Leader"})

            return self.users[index], 200
        else:
            return {
                "message" : "Missing user!"
            }, 404


    def delete_user(self, index : str):
        if index in self.users:
            user_dict = self.users.pop(index)

            if self.leader:
                for follower in self.followers:
                    requests.delete(f"https://{follower['host']}:{follower['port']}/user/{index}",
                                    headers = {"Token" : "Leader"})

            return user_dict, 200
        else:
            return {
                "message" : "Missing user!"
            }, 404