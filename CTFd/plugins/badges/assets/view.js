CTFd._internal.badge.data = undefined

CTFd._internal.badge.renderer = CTFd.lib.markdown();


CTFd._internal.badge.preRender = function () { }

CTFd._internal.badge.render = function (markdown) {
    return CTFd._internal.badge.renderer.render(markdown)
}


CTFd._internal.badge.postRender = function () { }


CTFd._internal.badge.submit = function (preview) {
    var badge_id = parseInt(CTFd.lib.$('#badge-id').val())
    var submission = CTFd.lib.$('#badge-input').val()

    var body = {
        'badge_id': badge_id,
        'submission': submission,
    }
    var params = {}
    if (preview) {
        params['preview'] = true
    }

    return CTFd.api.post_badge_attempt(params, body).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
        }
        return response
    })
};
