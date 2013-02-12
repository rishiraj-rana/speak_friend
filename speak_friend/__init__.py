from pyramid.config import Configurator
from pyramid.events import BeforeRender

from sqlalchemy import engine_from_config

from speak_friend.models import DBSession, Base
from speak_friend.views import profiles
from speak_friend.subscribers import register_api



def includeme(config):
    # Placeholder for now.
    config.add_route('create_profile', '/create_profile')
    config.add_view(profiles.CreateProfile, attr="get", request_method='GET',
                    renderer='templates/create_profile.pt')
    config.add_view(profiles.CreateProfile, attr="post", request_method='POST',
                    renderer='templates/create_profile.pt')
    config.add_subscriber(register_api, BeforeRender)

    config.add_static_view('static', 'deform:static')
    config.include('pyramid_exclog')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)

    # Includes for any packages that hook into configuration.
    config.include('pyramid_tm')

    # Extending an existing package allows you to override
    # view mappings and other configuration details.
    # config.include('base_package_name')

    # overriding templates should be done as follows:

    # config.override_asset('base_package_name:templates/base.pt',
    #                       'speak_friend:templates/override.pt')

    # Configuring URLs
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    includeme(config)
    config.scan()

    return config.make_wsgi_app()
