from social_core.backends.google import GoogleOAuth2
from social_core.backends.vk import VKOAuth2
from social_core.utils import module_member


class CustomGoogleOAuth2(GoogleOAuth2):
    def get_user_details(self, response):
        """Return user details from Google API account. Переопределил для извлечения аватара (picture)"""
        if 'email' in response:
            email = response['email']
        else:
            email = ''
        # print(response, 'ETO RESPONSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # print(self.__dict__)
        # print(self.__dict__.get('strategy').__dict__)
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

    # def process_error(self, data):
    #     print('!' * 100)
    #     print(self)
    #     print(data)
    #     print('!' * 100)
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
            print(func, "ETO FUNC")
            print(out, '@'*100)
            print(args, '#'*100)
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
        print(response, 'ETO RESPONSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(self.__dict__)
        photo = (response.get('photo', ''))
        screen_name = (response.get('screen_name', ''))
        return {
                'username': response.get('screen_name'),
                'email': response.get('email', ''),
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name,
                'photo': photo,
                'vk_url': 'https://vk.com/' + screen_name}

    # def process_error(self, data):
    #     print('*' * 100)
    #     print(self)
    #     print(data)
    #     print('*' * 100)

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
            print(func, "ETO FUNC")
            print(out, '@'*100)
            print(args, '#'*100)
            result = func(*args, **out) or {}
            if not isinstance(result, dict):
                return result
            out.update(result)
        return out