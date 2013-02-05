# Views related to account management (creating, editing, deactivating)


from speak_friend.forms.profiles import profile_form


def create_profile(request):
    form = profile_form.render()
    return {'form': form}


def edit_profile(request):
    form = profile_form.render()
    return {'form': form}


def token_expired(request):
    request.response.status = "400 Bad Request"
    return {'message': u'That token has expired'}
