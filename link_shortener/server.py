'''
Copyright (C) 2020 Link Shortener Authors (see AUTHORS in Documentation).
Licensed under the MIT (Expat) License (see LICENSE in Documentation).
'''
from decouple import config

from sanic import Sanic

from sanic_oauth.blueprint import oauth_blueprint

from sanic_session import InMemorySessionInterface

from link_shortener.core.initialise_db import initdb_blueprint
from link_shortener.core.authentication import auth_blueprint

from link_shortener.form_routes import form_blueprint
from link_shortener.view_routes import view_blueprint
from link_shortener.api.retrieve import api_retrieve_blueprint


async def add_session_to_request(request):
    await request.app.session_interface.open(request)


async def save_session(request, response):
    '''
    See SESSION_ERROR in Documentation.
    '''
    try:
        user_info = request['session']['user_info']
        try:
            # request['session']['user_info'] = {'email': user_info.email}
            request['session']['user_info'] = dict(
                [
                    (attr, getattr(user_info, attr))
                    for attr in user_info.default_attrs
                ]
            )
        except AttributeError:
            pass
    except KeyError:
        pass

    await request.app.session_interface.save(request, response)


def create_app():
    app = Sanic(__name__)

    # ----------------------------------------------------------------------------
    # CONFIGURATION
    # ----------------------------------------------------------------------------

    app.blueprint(initdb_blueprint)
    app.blueprint(oauth_blueprint)
    app.blueprint(auth_blueprint)
    app.blueprint(form_blueprint)
    app.blueprint(view_blueprint)
    app.blueprint(api_retrieve_blueprint)

    app.static('/links/', './static/')
    app.config.WTF_CSRF_SECRET_KEY = config('WTF_CSRF_SECRET_KEY')

    # ----------------------------------------------------------------------------
    # AUTHENTICATION
    # ----------------------------------------------------------------------------

    app.session_interface = InMemorySessionInterface()

    app.config.OAUTH_PROVIDER = config('OAUTH_PROVIDER')
    app.config.OAUTH_REDIRECT_URI = config('OAUTH_REDIRECT_URI')
    app.config.OAUTH_SCOPE = config('OAUTH_SCOPE')
    app.config.OAUTH_CLIENT_ID = config('OAUTH_CLIENT_ID')
    app.config.OAUTH_CLIENT_SECRET = config('OAUTH_CLIENT_SECRET')

    app.register_middleware(add_session_to_request, 'request')
    app.register_middleware(save_session, 'response')

    return app


if (__name__ == '__main__'):
    app = create_app()
    app.run(host='0.0.0.0', port=8000)
