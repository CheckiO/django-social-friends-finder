from social_friends_finder.backends import BaseFriendsProvider
from social_friends_finder.utils import setting
if setting("SOCIAL_FRIENDS_USING_ALLAUTH", False):
    from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
    USING_ALLAUTH = True
else:
    from social_auth.backends.twitter import TwitterBackend
    USING_ALLAUTH = False
from django.conf import settings
from twython import Twython


class TwitterFriendsProvider(BaseFriendsProvider):

    def _auth_data(self, user):
        if USING_ALLAUTH:
            social_app = SocialApp.objects.get_current('twitter')
            auth_data = {'app_key': social_app.key,
                         'app_secret': social_app.secret,
                         'oauth_token': SocialToken.objects.get(account=user, app=social_app).token,
                         'oauth_token_secret': SocialToken.objects.get(account=user, app=social_app).token_secret}

        else:
            t = TwitterBackend()
            tokens = t.tokens(user)
            auth_data = {'app_key': settings.TWITTER_CONSUMER_KEY,
                         'app_secret': settings.TWITTER_CONSUMER_SECRET,
                         'oauth_token': tokens['oauth_token'],
                         'oauth_token_secret': tokens['oauth_token_secret']}

        return auth_data

    def fetch_friends(self, user):
        """
        fetches the friends from twitter using the
        information on django-social-auth models
        user is an instance of UserSocialAuth

        Returns:
            collection of friend objects fetched from Twitter
        """

        # now fetch the twitter friends using `twython`
        auth_data = self._auth_data(user)
        tw = Twython(**auth_data)
        cursor = -1
        friends = []
        while True:
            data = tw.getFriendsList(cursor=cursor)
            friends += data.get('users', [])

            next_cursor = data.get('next_cursor', 0)
            prev_cursor = data.get('prev_cursor', 0)
            if not next_cursor or next_cursor == prev_cursor:
                break
            else:
                cursor = next_cursor
        return friends

    def fetch_friend_ids(self, user):
        """
        fetches friend id's from twitter

        Return:
            collection of friend ids
        """
        auth_data = self._auth_data(user)
        tw = Twython(**auth_data)
        cursor = -1
        friend_ids = []
        while True:
            data = tw.getFriendsIDs(cursor=cursor)
            friend_ids += data.get('ids', [])

            next_cursor = data.get('next_cursor', 0)
            prev_cursor = data.get('prev_cursor', 0)
            if not next_cursor or next_cursor == prev_cursor:
                break
            else:
                cursor = next_cursor
        return friend_ids
