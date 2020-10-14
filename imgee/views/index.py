# -*- coding: utf-8 -*-
from sqlalchemy import not_

from flask import Markup, abort, flash, redirect, render_template

from coaster.auth import current_auth
from coaster.views import (
    ModelView,
    UrlChangeCheck,
    UrlForView,
    requestargs,
    render_with,
    route,
)

from .. import app, forms, lastuser
from ..models import Label, Profile, StoredFile, db
from ..storage import clean_local_cache
from ..utils import ALLOWED_MIMETYPES, abort_null


@app.context_processor
def global_vars():
    cl_form = forms.CreateLabelForm()
    return {'cl_form': cl_form, 'uf_form': forms.UploadImageForm()}


@app.route('/')
def index():
    return render_template('index.html.jinja2')


@app.route('/account')
@lastuser.requires_login
def account():
    lastuser.update_user(current_auth.user)
    Profile.update_from_user(
        current_auth.user, db.session, make_user_profiles=True, make_org_profiles=True
    )
    db.session.commit()
    return redirect(current_auth.user.profile_url)


@route('/<profile>')
class ProfileView(UrlChangeCheck, UrlForView, ModelView):
    model = Profile
    route_model_map = {'profile': 'name'}
    UploadImageForm = forms.UploadImageForm

    def loader(self, profile):
        profileobj = Profile.query.filter_by(name=profile).one_or_none()
        if profileobj is None:
            # if there is a logged in user with same username as
            # the given profile name, create the profile
            if current_auth.user and current_auth.user.username == profile:
                profileobj = Profile(
                    name=profile,
                    title=current_auth.user.fullname,
                    userid=current_auth.user.userid,
                )
                db.session.add(profileobj)
                db.session.commit()
            else:
                abort(404)
        return profileobj

    @route('')
    @render_with('profile.html.jinja2')
    def view(self):
        files = self.obj.stored_files.order_by(db.desc(StoredFile.created_at)).all()
        title_form = forms.EditTitleForm()
        upload_form = forms.UploadImageForm()
        return {
            'profile': self.obj,
            'files': files,
            'uploadform': upload_form,
            'title_form': title_form,
            'mimetypes': ALLOWED_MIMETYPES.keys(),
        }

    @route('archive')
    @render_with('profile.html.jinja2')
    def unlabelled_images(self):
        """Get all unlabelled images owned by profile"""
        files = (
            self.obj.stored_files.filter(not_(StoredFile.labels.any()))
            .order_by(StoredFile.created_at.desc())
            .all()
        )
        title_form = forms.EditTitleForm()
        return {
            'profile': self.obj,
            'files': files,
            'title_form': title_form,
            'unlabelled': True,
        }

    @route('popup')
    @lastuser.requires_login
    @render_with('pop_up_gallery.html.jinja2')
    @requestargs(('label', abort_null))
    def pop_up_gallery(self, label=''):
        files = self.obj.stored_files
        if label:
            files = files.join(StoredFile.labels).filter(Label.name == label)
        files = files.order_by(StoredFile.created_at.desc())[:10]
        return (
            {
                'files': Markup(
                    '\n'.join(
                        [
                            render_template('pop_up_gallery_file.html.jinja2', img=img)
                            for img in files
                        ]
                    )
                ),
                'label': label,
                'profile': self.obj,
            },
            200,
            {'X-Frame-Options': 'ALLOW'},
        )

    @route('popup/files')
    @lastuser.requires_login
    @requestargs(('label', abort_null), ('page', int), ('per_page', int))
    def pop_up_files(self, label='', page=None, per_page=10):
        files = self.obj.stored_files
        files = files.order_by(db.desc(StoredFile.created_at))
        if label:
            files = files.join(StoredFile.labels).filter(Label.name == label)
        files = files.paginate(page=page, per_page=per_page)
        data = {
            'current_page': files.page,
            'total_pages': files.pages,
            'files': Markup(
                '\n'.join(
                    [
                        render_template('pop_up_gallery_file.html.jinja2', img=img)
                        for img in files.items
                    ]
                )
            ),
        }
        if files.pages > files.page:
            data['next_url'] = self.obj.url_for(
                'pop_up_files', page=files.page + 1, _external=True
            )
        return data


ProfileView.init_app(app)


def get_prev_next_images(profile, img, limit=2):
    # query for "all" images though we need just the `limit`
    # bcoz we don't know how many are there in deleteQ.
    prev_img = (
        profile.stored_files.filter(
            StoredFile.created_at <= img.created_at, StoredFile.id != img.id
        )
        .order_by(db.desc(StoredFile.created_at))
        .limit(limit)
        .all()
    )
    next_img = (
        profile.stored_files.filter(
            StoredFile.created_at >= img.created_at, StoredFile.id != img.id
        )
        .order_by(db.asc(StoredFile.created_at))
        .limit(limit)
        .all()
    )
    return prev_img, next_img


@app.route('/_admin/purge-cache', methods=['GET', 'POST'])
@lastuser.requires_login
@lastuser.requires_permission('siteadmin')
def purge_cache():
    form = forms.PurgeCacheForm()
    if form.is_submitted():
        removed = clean_local_cache(app.config.get('CACHE_PURGE_PERIOD', 24))
        flash('%s files are deleted from the cache.' % removed)
    return render_template('purge_cache.html.jinja2', form=form)
