from player import Player

import xml.etree.ElementTree as ET
from datetime import datetime

import generated.player_pb2 as player_proto


class PlayerFactory:
    
    def to_json(self, players):
        serialized_players = list()
        for player in players:
            serialized_players.append({
                "nickname": player.nickname,
                "email": player.email,
                "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d"),
                "xp": player.xp,
                "class": player.cls
            })
        
        return serialized_players


    def from_json(self, list_of_dict):
        deserialized_players = list()
        for json_player in list_of_dict:
            player = Player(json_player['nickname'], json_player['email'],
                            json_player['date_of_birth'], json_player['xp'],
                            json_player['class'])
            deserialized_players.append(player)

        return deserialized_players


    def from_xml(self, xml_string):
        root = ET.fromstring(xml_string)

        deserialized_players = list()
        for xml_player in root.findall("player"):
            nickname = xml_player.find("nickname").text
            email = xml_player.find("email").text
            date_of_birth = datetime.strptime(xml_player.find("date_of_birth").text, "%Y-%m-%d")
            xp = int(xml_player.find("xp").text)
            player_class = xml_player.find("class").text
            
            player = Player(nickname, email, date_of_birth, xp, player_class)
            deserialized_players.append(player)
        
        return deserialized_players


    def to_xml(self, list_of_players):
        player_config = ET.Element("data")
 
        for player in list_of_players:
            pl = ET.SubElement(player_config, "player")
            nickname = ET.SubElement(pl, 'nickname')
            nickname.text = player.nickname

            email = ET.SubElement(pl, 'email')
            email.text = player.email

            date_of_birth = ET.SubElement(pl, 'date_of_birth')
            date_of_birth.text = player.date_of_birth.strftime("%Y-%m-%d")

            xp = ET.SubElement(pl, 'xp')
            xp.text = str(player.xp)

            cls = ET.SubElement(pl, 'class')
            cls.text = player.cls
 
        return ET.tostring(player_config)

    '''
    def json_to_xml(self, list_of_dicts):
        list_of_players = list()
        for json_player in list_of_dicts:
            list_of_players.append(Player(json_player['nickname'], json_player['email'],
                            json_player['date_of_birth'], json_player['xp'],
                            json_player['class']))
            
        player_config = ET.Element("data")
 
        for player in list_of_players:
            pl = ET.SubElement(player_config, "player")
            nickname = ET.SubElement(pl, 'nickname')
            nickname.text = player.nickname

            email = ET.SubElement(pl, 'email')
            email.text = player.email

            date_of_birth = ET.SubElement(pl, 'date_of_birth')
            date_of_birth.text = player.date_of_birth.strftime("%Y-%m-%d")

            xp = ET.SubElement(pl, 'xp')
            xp.text = str(player.xp)

            cls = ET.SubElement(pl, 'class')
            cls.text = player.cls
 
        return ET.tostring(player_config)
        

    def xml_to_json(self, xml_string):
        root = ET.fromstring(xml_string)

        deserialized_players = list()
        for xml_player in root.findall("player"):
            nickname = xml_player.find("nickname").text
            email = xml_player.find("email").text
            date_of_birth = datetime.strptime(xml_player.find("date_of_birth").text, "%Y-%m-%d")
            xp = int(xml_player.find("xp").text)
            player_class = xml_player.find("class").text
            
            player = Player(nickname, email, date_of_birth, xp, player_class)
            deserialized_players.append(player)

        # TODO : finish 
    '''

    def from_protobuf(self, binary):
        list_of_players = player_proto.PlayersList()
        list_of_players.ParseFromString(binary)
        
        p_list = []
        for player in list_of_players.player:
            cls = ''
            if player.cls == 0:
                cls = 'Berserk'
            elif player.cls == 1:
                cls = 'Tank'
            elif player.cls == 3:
                cls = 'Paladin'
            else:
                cls = 'Mage'

            p = Player(player.nickname, player.email, player.date_of_birth,
                       player.xp, cls)
            
            p_list.append(p)

        return p_list


    def to_protobuf(self, list_of_players):
        p_list = player_proto.PlayersList()
        for player in list_of_players:
            p = p_list.player.add()
            p.nickname = player.nickname
            p.email = player.email
            p.date_of_birth = player.date_of_birth.strftime("%Y-%m-%d")
            p.xp = player.xp
            
            if player.cls == 'Berserk':
                p.cls = player_proto.Class.Berserk
            elif player.cls == 'Tank':
                p.cls = player_proto.Class.Tank
            elif player.cls == 'Paladin':
                p.cls = player_proto.Class.Paladin
            else:
                p.cls = player_proto.Class.Mage
        
        return p_list.SerializeToString()