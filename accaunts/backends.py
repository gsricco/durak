import urllib.request

import vk_api
from social_core.backends.google import GoogleOAuth2
from social_core.backends.vk import VKOAuth2
from social_core.utils import module_member

from configs.settings import VK_TOKEN

access_token = VK_TOKEN
user_id = '363914012'

class CustomGoogleOAuth2(GoogleOAuth2):
    def get_user_details(self, response):
        """Return user details from Google API account. Переопределил для извлечения аватара (picture)"""
        print(response)
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
        return {'username': email,
                'email': email,
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name,
                'photo': picture,
                'usernamegame': first_name + ' ' + last_name
                }

    def run_pipeline(self, pipeline, pipeline_index=0, *args, **kwargs):
        out = kwargs.copy()
        out.setdefault('strategy', self.strategy)
        out.setdefault('backend', out.pop(self.name, None) or self)
        out.setdefault('request', self.strategy.request_data())
        out.setdefault('details', {})

        if not isinstance(pipeline_index, int) or \
                pipeline_index < 0 or \
                pipeline_index >= len(pipeline):
            pipeline_index = 0

        for idx, name in enumerate(pipeline[pipeline_index:]):
            out['pipeline_index'] = pipeline_index + idx
            func = module_member(name)
            result = func(*args, **out) or {}
            if not isinstance(result, dict):
                return result
            out.update(result)
        return out


class CustomVKOAuth2(VKOAuth2):
    def get_user_details(self, response):
        """Return user details from VK.com account. Переопределил для извлечения аватара (picture)"""
        fullname, first_name, last_name = self.get_user_names(
            first_name=response.get('first_name'),
            last_name=response.get('last_name')
        )
        photo = self.get_vk_photo(response.get("user_id"))
        screen_name = (response.get('screen_name', ''))
        user_id = response.get('id')
        user_name = self.check_name(user_id, screen_name, first_name, last_name)
        return {
                'username': str(response.get('id')),
                'email': response.get('email', ''),
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name,
                'photo': photo,
                'vk_url': 'https://vk.com/' + screen_name,
                'usernamegame': first_name + ' ' + last_name
        }


    def check_name(self, user_id, screen_name, first_name, last_name):
        if str(user_id) not in screen_name:
            return screen_name
        else:
            return first_name + ' ' + last_name

    def get_vk_photo(self, user_id):
        vk_session = vk_api.VkApi(token=access_token)
        response = vk_session.method('users.get', {'user_ids': user_id, 'fields': 'photo_max'})
        photo_url = response[0]['photo_max']
        return photo_url


    def run_pipeline(self, pipeline, pipeline_index=0, *args, **kwargs):
        out = kwargs.copy()
        out.setdefault('strategy', self.strategy)
        out.setdefault('backend', out.pop(self.name, None) or self)
        out.setdefault('request', self.strategy.request_data())
        out.setdefault('details', {})

        if not isinstance(pipeline_index, int) or \
                pipeline_index < 0 or \
                pipeline_index >= len(pipeline):
            pipeline_index = 0

        for idx, name in enumerate(pipeline[pipeline_index:]):
            out['pipeline_index'] = pipeline_index + idx
            func = module_member(name)
            result = func(*args, **out) or {}
            if not isinstance(result, dict):
                return result
            out.update(result)
        return out