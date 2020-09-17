import re
from django.contrib.auth.models import User

class MentionsHandler:

    def check_for_mentions(text):
        """
        :param text: post text in form of string
        :return: new string where mentions (@username) are replaced with links
        """
        split_str = text.split()
        new_str = ""
        pattern = re.compile("^@[a-zA-Z]*$")
        for word in split_str:
            if pattern.match(word):
                try:
                    user = User.objects.get(username=word[1:])
                    if user:
                        word = MentionsHandler.urlify_mention(word)
                except User.DoesNotExist:
                    pass
            new_str += word + " "
        new_str = new_str[:-1]
        return new_str

    def urlify_mention(username):
        """
        :param username: string in format @username
        :return: string that will represent an url in markdown format
        """
        name = username[1:]
        if name != "":
            urlified_username = "[" + username + "](/accounts/profile/" + name + ")"
            return urlified_username
        else:
            return username