def get_prompt_from_command(text, client):
    #remove tag of praise bot

    #add spacing if there's multiple users
    text = text.replace("><@", "> and <@")
    text = text.replace("> <@", "> and <@")

    #replace tags with user's real name
    while("<@" in text):
        text = replaceMention(text, client)
    return text

def replaceMention(text, client):
    if "<@" in text:
        mention = text[text.find("<@"):text.find("|")+1]
        removal = text[text.find("<@"):text.find(">")+1]
        name = getNameFromMention(text, client)
        text = text.replace(removal, name)
        return text
    else:
        return text
    
def getNameFromMention(text, client):
    if "<@" in text:
        mention = text[text.find("<@"):text.find("|")+1]
        user_id = mention[2:-1]
        user = client.users_info(user=user_id)
        name = user['user']['real_name']
        return name
    else:
        return text
    
def get_users_from_command(text):
    users = []
    while("<@" in text):
        startIndex = text.find("<@")
        endIndex = text.find("|")
        mention = text[startIndex+2:endIndex]
        users.append(mention)
        text = text.replace(text[startIndex:endIndex+1], "")
    return users

def getNameFromUserId(user_id, client):
    print("userID" + user_id)
    user = client.users_info(user=user_id)
    name = user['user']['real_name']
    return name