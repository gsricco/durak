from social_core.backends.google import GoogleOAuth2
from social_core.backends.vk import VKOAuth2


class CustomGoogleOAuth2(GoogleOAuth2):
    def get_user_details(self, response):
        """Return user details from Google API account. Переопределил для извлечения аватара (picture)"""
        if 'email' in response:
            email = response['email']
        else:
            email = ''

        name, given_name, family_name, picture = (
            response.get('name', ''),
            response.get('given_name', ''),
            response.get('family_name', ''),
            response.get('picture', ''),
        )

        fullname, first_name, last_name = self.get_user_names(
            name, given_name, family_name
        )
        return {'username': email.split('@', 1)[0],
                'email': email,
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name,
                'photo': picture}


class CustomVKOAuth2(VKOAuth2):
    def get_user_details(self, response):
        """Return user details from VK.com account. Переопределил для извлечения аватара (picture)"""
        fullname, first_name, last_name = self.get_user_names(
            first_name=response.get('first_name'),
            last_name=response.get('last_name')
        )
        photo = (response.get('photo', ''))
        screen_name = (response.get('screen_name', ''))
        return {
                'username': response.get('screen_name'),
                'email': response.get('email', ''),
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name,
                'photo': photo,
                'vk_url': 'https://vk.com/' + screen_name
                }
