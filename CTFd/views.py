import os

from flask import Blueprint, abort
from flask import current_app as app
from flask import redirect, render_template, request, send_file, session, url_for
from flask.helpers import safe_join
from sqlalchemy.exc import IntegrityError

from CTFd.cache import cache
from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
)
from CTFd.constants.themes import DEFAULT_THEME
from CTFd.models import (
    Admins,
    Files,
    Notifications,
    Pages,
    Rights,
    Roles,
    RoleRights,
    UserRights,
    Users,
    UserTokens,
    db,
)
from CTFd.utils import config, get_config, set_config
from CTFd.utils import validators
from CTFd.utils.config.pages import build_html, get_page
from CTFd.utils.config.visibility import challenges_visible
from CTFd.utils.decorators import authed_only
from CTFd.utils.email import (
    DEFAULT_PASSWORD_RESET_BODY,
    DEFAULT_PASSWORD_RESET_SUBJECT,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    DEFAULT_USER_CREATION_EMAIL_BODY,
    DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    DEFAULT_VERIFICATION_EMAIL_BODY,
    DEFAULT_VERIFICATION_EMAIL_SUBJECT,
)
from CTFd.utils.helpers import get_errors, get_infos, markup
from CTFd.utils.security.auth import login_user
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import (
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    serialize,
    unserialize,
)
from CTFd.utils.uploads import get_uploader, upload_file
from CTFd.utils.user import authed, get_current_user

views = Blueprint("views", __name__)


@views.route("/setup", methods=["GET", "POST"])
def setup():
    errors = get_errors()
    if not config.is_setup():
        if not session.get("nonce"):
            session["nonce"] = generate_nonce()
        if request.method == "POST":
            # General
            ctf_name = request.form.get("ctf_name")
            ctf_description = request.form.get("ctf_description")
            set_config("ctf_name", ctf_name)
            set_config("ctf_description", ctf_description)

            # Style
            ctf_logo = request.files.get("ctf_logo")
            if ctf_logo:
                f = upload_file(file=ctf_logo)
                set_config("ctf_logo", f.location)

            ctf_small_icon = request.files.get("ctf_small_icon")
            if ctf_small_icon:
                f = upload_file(file=ctf_small_icon)
                set_config("ctf_small_icon", f.location)

            theme = request.form.get("ctf_theme", DEFAULT_THEME)
            set_config("ctf_theme", theme)
            theme_color = request.form.get("theme_color")
            theme_header = get_config("theme_header")
            if theme_color and bool(theme_header) is False:
                # Uses {{ and }} to insert curly braces while using the format method
                css = (
                    '<style id="theme-color">\n'
                    ":root {{--theme-color: {theme_color};}}\n"
                    ".navbar{{background-color: var(--theme-color) !important;}}\n"
                    ".jumbotron{{background-color: var(--theme-color) !important;}}\n"
                    "</style>\n"
                ).format(theme_color=theme_color)
                set_config("theme_header", css)

            # Administration
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]

            name_len = len(name) == 0
            names = Users.query.add_columns("name", "id").filter_by(name=name).first()
            emails = (
                Users.query.add_columns("email", "id").filter_by(email=email).first()
            )
            pass_short = len(password) == 0
            pass_long = len(password) > 128
            valid_email = validators.validate_email(request.form["email"])

            if not valid_email:
                errors.append("Please enter a valid email address")
            if names:
                errors.append("That user name is already taken")
            if emails:
                errors.append("That email has already been used")
            if pass_short:
                errors.append("Pick a longer password")
            if pass_long:
                errors.append("Pick a shorter password")
            if name_len:
                errors.append("Pick a longer user name")

            if len(errors) > 0:
                return render_template(
                    "setup.html",
                    errors=errors,
                    name=name,
                    email=email,
                    password=password,
                    state=serialize(generate_nonce()),
                )

            admin = Admins(
                name=name, email=email, password=password, type="admin", hidden=True
            )

            # Create an empty index page
            page = Pages(title=None, route="index", content="", draft=False)

            # Upload banner
            default_ctf_banner_location = url_for("views.themes", path="img/logo.png")
            ctf_banner = request.files.get("ctf_banner")
            if ctf_banner:
                f = upload_file(file=ctf_banner, page_id=page.id)
                default_ctf_banner_location = url_for("views.files", path=f.location)

            # Splice in our banner
            index = f"""<div class="row">
    <div class="col-md-6 offset-md-3">
        <img class="w-100 mx-auto d-block" style="max-width: 500px;padding: 50px;padding-top: 14vh;" src="{default_ctf_banner_location}" />
        <h3 class="text-center">
            <p>A cool CTF platform from <a href="https://ctfd.io">ctfd.io</a></p>
            <p>Follow us on social media:</p>
            <a href="https://twitter.com/ctfdio"><i class="fab fa-twitter fa-2x" aria-hidden="true"></i></a>&nbsp;
            <a href="https://facebook.com/ctfdio"><i class="fab fa-facebook fa-2x" aria-hidden="true"></i></a>&nbsp;
            <a href="https://github.com/ctfd"><i class="fab fa-github fa-2x" aria-hidden="true"></i></a>
        </h3>
        <br>
        <h4 class="text-center">
            <a href="admin">Click here</a> to login and setup your CTF
        </h4>
    </div>
</div>"""

            page.content = index

            # Set up default number of positive votes
            set_config("votes_number_delta", 3)

            # Visibility
            set_config(
                ConfigTypes.CHALLENGE_VISIBILITY, ChallengeVisibilityTypes.PRIVATE
            )
            set_config(
                ConfigTypes.REGISTRATION_VISIBILITY, RegistrationVisibilityTypes.PUBLIC
            )
            set_config(ConfigTypes.ACCOUNT_VISIBILITY, AccountVisibilityTypes.PUBLIC)

            # Verify emails
            set_config("verify_emails", None)

            set_config("mail_server", None)
            set_config("mail_port", None)
            set_config("mail_tls", None)
            set_config("mail_ssl", None)
            set_config("mail_username", None)
            set_config("mail_password", None)
            set_config("mail_useauth", None)

            # Set up default emails
            set_config("verification_email_subject", DEFAULT_VERIFICATION_EMAIL_SUBJECT)
            set_config("verification_email_body", DEFAULT_VERIFICATION_EMAIL_BODY)

            set_config(
                "successful_registration_email_subject",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
            )
            set_config(
                "successful_registration_email_body",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
            )

            set_config(
                "user_creation_email_subject", DEFAULT_USER_CREATION_EMAIL_SUBJECT
            )
            set_config("user_creation_email_body", DEFAULT_USER_CREATION_EMAIL_BODY)

            set_config("password_reset_subject", DEFAULT_PASSWORD_RESET_SUBJECT)
            set_config("password_reset_body", DEFAULT_PASSWORD_RESET_BODY)

            set_config(
                "password_change_alert_subject",
                "Password Change Confirmation for {ctf_name}",
            )
            set_config(
                "password_change_alert_body",
                (
                    "Your password for {ctf_name} has been changed.\n\n"
                    "If you didn't request a password change you can reset your password here: {url}"
                ),
            )

            set_config("setup", True)

            try:
                db.session.add(admin)
                db.session.commit()

                # Store all rights
                new_rights = [
                    "admin_view",
                    "admin_plugin",
                    "admin_import_ctf",
                    "admin_export_ctf",
                    "admin_export_csv",
                    "admin_config",
                    "admin_reset",
                    "admin_challenges_listing",
                    "admin_challenges_listing_restricted",
                    "admin_challenges_detail",
                    "admin_challenges_new",
                    "admin_notifications",
                    "admin_pages_listing",
                    "admin_pages_new",
                    "admin_pages_preview",
                    "admin_pages_detail",
                    "admin_statistics",
                    "admin_submissions_listing",
                    "admin_user_listing",
                    "admin_users_new",
                    "admin_users_detail",
                    "api_award_list_get",
                    "api_award_list_post",
                    "api_award_get",
                    "api_award_delete",
                    "api_challenge_list_get",
                    "api_challenge_list_get_view_full",
                    "api_challenge_list_post",
                    "api_challenge_types_get",
                    "api_challenge_get",
                    "api_challenge_get_not_hidden",
                    "api_challenge_patch",
                    "api_challenge_patch_full",
                    "api_challenge_patch_partial",
                    "api_challenge_delete",
                    "api_challenge_attempt_post",
                    "api_challenge_attempt_post_full",
                    "api_challenge_solves_get",
                    "api_challenge_files_get",
                    "api_challenge_tags_get",
                    "api_challenge_hints_get",
                    "api_challenge_votes_get",
                    "api_challenge_votes_get_edit_vote",
                    "api_challenge_flags_get",
                    "api_challenge_requirements_get",
                    "api_comment_list_get",
                    "api_comment_list_post",
                    "api_comment_delete",
                    "api_config_list_get",
                    "api_config_list_post",
                    "api_config_list_patch",
                    "api_config_get",
                    "api_config_patch",
                    "api_config_delete",
                    "api_field_list_get",
                    "api_field_list_post",
                    "api_field_get",
                    "api_field_patch",
                    "api_field_delete",
                    "api_files_list_get",
                    "api_files_list_post",
                    "api_files_detail_get",
                    "api_files_detail_delete",
                    "api_flag_list_get",
                    "api_flag_list_post",
                    "api_flag_types_get",
                    "api_flag_get",
                    "api_flag_delete",
                    "api_flag_post",
                    "api_hint_list_get",
                    "api_hint_list_post",
                    "api_hint_get",
                    "api_hint_patch",
                    "api_hint_delete",
                    "api_notification_list_get",
                    "api_notification_list_post",
                    "api_notification_get",
                    "api_notification_delete",
                    "api_page_list_get",
                    "api_page_list_post",
                    "api_page_detail_get",
                    "api_page_detail_patch",
                    "api_page_detail_delete",
                    "api_role_rights_list_get",
                    "api_role_rights_list_post",
                    "api_role_rights_get",
                    "api_role_rights_delete",
                    "api_role_list_get",
                    "api_role_list_post",
                    "api_role_get",
                    "api_role_delete",
                    "api_submissions_list_get",
                    "api_submissions_list_post",
                    "api_submission_get",
                    "api_submission_delete",
                    "api_tag_challenge_list_get",
                    "api_tag_challenge_list_post",
                    "api_tag_challenge_list_post_restricted",
                    "api_tag_chal_get",
                    "api_tag_chal_delete",
                    "api_tag_list_get",
                    "api_tag_list_post",
                    "api_tag_list_post_restricted",
                    "api_tag_get",
                    "api_tag_patch",
                    "api_tag_delete",
                    "api_token_list_get",
                    "api_token_list_post",
                    "api_token_detail_get",
                    "api_token_detail_get_full",
                    "api_token_detail_delete",
                    "api_token_detail_delete_full",
                    "api_unlock_list_get",
                    "api_unlock_list_post",
                    "api_user_rights_list_get",
                    "api_user_rights_list_post",
                    "api_user_rights_get",
                    "api_user_rights_delete",
                    "api_user_list_get",
                    "api_user_list_get_full",
                    "api_user_list_post",
                    "api_user_public_get",
                    "api_user_public_get_full",
                    "api_user_public_patch",
                    "api_user_public_delete",
                    "api_user_private_get",
                    "api_user_private_patch",
                    "api_user_private_solves_get",
                    "api_user_private_solves_get_full",
                    "api_user_private_fails_get",
                    "api_user_private_fails_get_full",
                    "api_user_private_awards_get",
                    "api_user_private_awards_get_full",
                    "api_user_public_solves_get",
                    "api_user_public_solves_get_full",
                    "api_user_public_fails_get",
                    "api_user_public_fails_get_full",
                    "api_user_public_awards_get",
                    "api_user_public_awards_get_full",
                    "api_user_emails_post",
                    "api_vote_list_get",
                    "api_vote_list_post",
                    "api_vote_get",
                    "api_vote_delete",
                    "api_vote_delete_full",
                    "api_vote_delete_partial",
                    "api_vote_patch",
                    "api_vote_patch_full",
                    "api_vote_patch_partial",
                    "api_statistics_challenge_property_counts_get",
                    "api_statistics_challenge_solve_statistics_get",
                    "api_statistics_challenge_solve_percentages_get",
                    "api_statistics_submission_property_counts_get",
                    "api_statistics_user_statistics_get",
                    "api_statistics_user_property_counts_get",
                    "api_badge_get",
                    "api_badge_post",
                    "api_badge_patch",
                    "api_badge_delete",
                    "forms_user_edit_form_full",
                    "forms_user_edit_form_partial",
                    "forms_user_create_form_full",
                    "forms_user_create_form_partial",
                    "schemas_user_schema_validate_name",
                    "schemas_user_schema_validate_email",
                    "schemas_user_schema_validate_password_confirmation",
                    "schemas_user_schema_validate_type_full",
                    "schemas_user_schema_validate_type_partial",
                    "schemas_user_schema_validate_fields",
                    "theme_admin_templates_base_full",
                    "theme_admin_templates_base_partial",
                    "theme_admin_templates_challenges_challenge",
                    "theme_admin_templates_challenges_new",
                    "theme_admin_templates_challenges_update",
                    "utils_config_visibility_challenges_visible",
                    "utils_config_visibility_accounts_visible",
                    "utils_decorators_require_verified_emails",
                    "utils_decorators_visibility_check_challenge_visibility",
                    "utils_decorators_visibility_check_account_visibility",
                    "utils_validators_unique_email",
                ]

                rights = []
                for new_right in new_rights:
                    right = Rights(name=new_right)
                    rights.append(right)
                db.session.add_all(rights)

                admin_rights = [
                    "admin_view",
                    "admin_plugin",
                    "admin_import_ctf",
                    "admin_export_ctf",
                    "admin_export_csv",
                    "admin_config",
                    "admin_reset",
                    "admin_challenges_listing",
                    "admin_challenges_detail",
                    "admin_challenges_new",
                    "admin_notifications",
                    "admin_pages_listing",
                    "admin_pages_new",
                    "admin_pages_preview",
                    "admin_pages_detail",
                    "admin_statistics",
                    "admin_submissions_listing",
                    "admin_user_listing",
                    "admin_users_new",
                    "admin_users_detail",
                    "api_award_list_get",
                    "api_award_list_post",
                    "api_award_get",
                    "api_award_delete",
                    "api_challenge_list_get",
                    "api_challenge_list_get_view_full",
                    "api_challenge_list_post",
                    "api_challenge_types_get",
                    "api_challenge_get",
                    "api_challenge_get_not_hidden",
                    "api_challenge_patch",
                    "api_challenge_patch_full",
                    "api_challenge_delete",
                    "api_challenge_attempt_post",
                    "api_challenge_attempt_post_full",
                    "api_challenge_solves_get",
                    "api_challenge_files_get",
                    "api_challenge_tags_get",
                    "api_challenge_hints_get",
                    "api_challenge_votes_get",
                    "api_challenge_votes_get_edit_vote",
                    "api_challenge_flags_get",
                    "api_challenge_requirements_get",
                    "api_comment_list_get",
                    "api_comment_list_post",
                    "api_comment_delete",
                    "api_config_list_get",
                    "api_config_list_post",
                    "api_config_list_patch",
                    "api_config_get",
                    "api_config_patch",
                    "api_config_delete",
                    "api_field_list_get",
                    "api_field_list_post",
                    "api_field_get",
                    "api_field_patch",
                    "api_field_delete",
                    "api_files_list_get",
                    "api_files_list_post",
                    "api_files_detail_get",
                    "api_files_detail_delete",
                    "api_flag_list_get",
                    "api_flag_list_post",
                    "api_flag_types_get",
                    "api_flag_get",
                    "api_flag_delete",
                    "api_flag_post",
                    "api_hint_list_get",
                    "api_hint_list_post",
                    "api_hint_get",
                    "api_hint_patch",
                    "api_hint_delete",
                    "api_notification_list_get",
                    "api_notification_list_post",
                    "api_notification_get",
                    "api_notification_delete",
                    "api_page_list_get",
                    "api_page_list_post",
                    "api_page_detail_get",
                    "api_page_detail_patch",
                    "api_page_detail_delete",
                    "api_role_rights_list_get",
                    "api_role_rights_list_post",
                    "api_role_rights_get",
                    "api_role_rights_delete",
                    "api_role_list_get",
                    "api_role_list_post",
                    "api_role_get",
                    "api_role_delete",
                    "api_submissions_list_get",
                    "api_submissions_list_post",
                    "api_submission_get",
                    "api_submission_delete",
                    "api_tag_challenge_list_get",
                    "api_tag_challenge_list_post",
                    "api_tag_chal_get",
                    "api_tag_chal_delete",
                    "api_tag_list_post",
                    "api_tag_get",
                    "api_tag_patch",
                    "api_tag_delete",
                    "api_token_list_get",
                    "api_token_list_post",
                    "api_token_detail_get",
                    "api_token_detail_get_full",
                    "api_token_detail_delete",
                    "api_token_detail_delete_full",
                    "api_unlock_list_get",
                    "api_unlock_list_post",
                    "api_user_rights_list_get",
                    "api_user_rights_list_post",
                    "api_user_rights_get",
                    "api_user_rights_delete",
                    "api_user_list_get",
                    "api_user_list_get_full",
                    "api_user_list_post",
                    "api_user_public_get",
                    "api_user_public_get_full",
                    "api_user_public_patch",
                    "api_user_public_delete",
                    "api_user_private_get",
                    "api_user_private_patch",
                    "api_user_private_solves_get",
                    "api_user_private_solves_get_full",
                    "api_user_private_fails_get",
                    "api_user_private_fails_get_full",
                    "api_user_private_awards_get",
                    "api_user_private_awards_get_full",
                    "api_user_public_solves_get",
                    "api_user_public_solves_get_full",
                    "api_user_public_fails_get",
                    "api_user_public_fails_get_full",
                    "api_user_public_awards_get",
                    "api_user_public_awards_get_full",
                    "api_user_emails_post",
                    "api_vote_list_get",
                    "api_vote_list_post",
                    "api_vote_get",
                    "api_vote_delete",
                    "api_vote_delete_full",
                    "api_vote_patch",
                    "api_vote_patch_full",
                    "api_statistics_challenge_property_counts_get",
                    "api_statistics_challenge_solve_statistics_get",
                    "api_statistics_challenge_solve_percentages_get",
                    "api_statistics_submission_property_counts_get",
                    "api_statistics_user_statistics_get",
                    "api_statistics_user_property_counts_get",
                    "api_badge_get",
                    "api_badge_post",
                    "api_badge_patch",
                    "api_badge_delete",
                    "forms_user_edit_form_full",
                    "forms_user_edit_form_partial",
                    "forms_user_create_form_full",
                    "forms_user_create_form_partial",
                    "schemas_user_schema_validate_name",
                    "schemas_user_schema_validate_email",
                    "schemas_user_schema_validate_password_confirmation",
                    "schemas_user_schema_validate_type_full",
                    "schemas_user_schema_validate_type_partial",
                    "schemas_user_schema_validate_fields",
                    "theme_admin_templates_base_full",
                    "theme_admin_templates_base_partial",
                    "theme_admin_templates_challenges_challenge",
                    "theme_admin_templates_challenges_new",
                    "theme_admin_templates_challenges_update",
                    "utils_config_visibility_challenges_visible",
                    "utils_config_visibility_accounts_visible",
                    "utils_decorators_require_verified_emails",
                    "utils_decorators_visibility_check_challenge_visibility",
                    "utils_decorators_visibility_check_account_visibility",
                    "utils_validators_unique_email",
                ]

                teacher_rights = [
                    "admin_view",
                    "admin_challenges_listing",
                    "admin_challenges_detail",
                    "admin_challenges_new",
                    "admin_user_listing",
                    "admin_users_new",
                    "admin_users_detail",
                    "api_challenge_list_get",
                    "api_challenge_list_post",
                    "api_challenge_types_get",
                    "api_challenge_patch",
                    "api_challenge_patch_full",
                    "api_challenge_delete",
                    "api_challenge_attempt_post",
                    "api_challenge_files_get",
                    "api_challenge_tags_get",
                    "api_challenge_hints_get",
                    "api_challenge_votes_get",
                    "api_challenge_flags_get",
                    "api_challenge_requirements_get",
                    "api_comment_list_get",
                    "api_comment_list_post",
                    "api_comment_delete",
                    "api_files_list_get",
                    "api_files_list_post",
                    "api_files_detail_get",
                    "api_files_detail_delete",
                    "api_flag_list_get",
                    "api_flag_list_post",
                    "api_flag_types_get",
                    "api_flag_get",
                    "api_flag_delete",
                    "api_flag_post",
                    "api_hint_list_get",
                    "api_hint_list_post",
                    "api_hint_get",
                    "api_hint_patch",
                    "api_hint_delete",
                    "api_notification_list_get",
                    "api_notification_get",
                    "api_tag_challenge_list_get",
                    "api_tag_challenge_list_post",
                    "api_tag_chal_get",
                    "api_tag_chal_delete",
                    "api_tag_list_post",
                    "api_tag_get",
                    "api_tag_patch",
                    "api_tag_delete",
                    "api_token_list_get",
                    "api_token_list_post",
                    "api_token_detail_get",
                    "api_token_detail_delete",
                    "api_unlock_list_post",
                    "api_user_list_get",
                    "api_user_list_post",
                    "api_user_public_get",
                    "api_user_public_patch",
                    "api_user_public_delete",
                    "api_user_private_get",
                    "api_user_private_patch",
                    "api_user_private_solves_get",
                    "api_user_private_fails_get",
                    "api_user_private_awards_get",
                    "api_user_public_solves_get",
                    "api_user_public_fails_get",
                    "api_user_public_awards_get",
                    "api_vote_list_get",
                    "api_vote_list_post",
                    "api_vote_get",
                    "api_vote_delete",
                    "api_vote_delete_partial",
                    "api_vote_patch",
                    "api_vote_patch_partial",
                    "api_statistics_user_statistics_get",
                    "api_statistics_user_property_counts_get",
                    "api_badge_get",
                    "api_badge_post",
                    "api_badge_patch",
                    "api_badge_delete",
                    "forms_user_edit_form_partial",
                    "forms_user_create_form_partial",
                    "schemas_user_schema_validate_name",
                    "schemas_user_schema_validate_email",
                    "schemas_user_schema_validate_password_confirmation",
                    "schemas_user_schema_validate_type_partial",
                    "schemas_user_schema_validate_fields",
                    "theme_admin_templates_base_partial",
                    "theme_admin_templates_challenges_challenge",
                    "theme_admin_templates_challenges_new",
                    "theme_admin_templates_challenges_update",
                ]

                contributor_rights = [
                    "admin_view",
                    "admin_challenges_listing",
                    "admin_challenges_listing_restricted",
                    "admin_challenges_new",
                    "api_challenge_list_get",
                    "api_challenge_list_post",
                    "api_challenge_types_get",
                    "api_challenge_patch",
                    "api_challenge_attempt_post",
                    "api_challenge_files_get",
                    "api_challenge_tags_get",
                    "api_challenge_hints_get",
                    "api_challenge_votes_get",
                    "api_challenge_flags_get",
                    "api_challenge_requirements_get",
                    "api_comment_list_get",
                    "api_comment_list_post",
                    "api_files_list_get",
                    "api_files_list_post",
                    "api_files_detail_get",
                    "api_files_detail_delete",
                    "api_flag_list_get",
                    "api_flag_list_post",
                    "api_flag_types_get",
                    "api_flag_get",
                    "api_hint_list_get",
                    "api_hint_get",
                    "api_notification_list_get",
                    "api_notification_get",
                    "api_tag_challenge_list_get",
                    "api_tag_challenge_list_post",
                    "api_tag_challenge_list_post_restricted",
                    "api_tag_chal_get",
                    "api_tag_chal_delete",
                    "api_tag_list_post",
                    "api_tag_list_post_restricted",
                    "api_tag_get",
                    "api_token_list_get",
                    "api_token_list_post",
                    "api_token_detail_get",
                    "api_token_detail_delete",
                    "api_unlock_list_post",
                    "api_user_list_get",
                    "api_user_public_get",
                    "api_user_private_get",
                    "api_user_private_patch",
                    "api_user_private_solves_get",
                    "api_user_private_fails_get",
                    "api_user_private_awards_get",
                    "api_user_public_solves_get",
                    "api_user_public_fails_get",
                    "api_user_public_awards_get",
                    "api_vote_list_get",
                    "api_vote_list_post",
                    "api_vote_get",
                    "api_vote_delete",
                    "api_vote_delete_partial",
                    "api_vote_patch",
                    "api_vote_patch_partial",
                    "api_badge_get",
                    "api_badge_post",
                    "api_badge_patch",
                    "api_badge_delete",
                ]

                # Create the new roles
                admin_role = Roles(name="admin")
                db.session.add(admin_role)
                teacher_role = Roles(name="teacher")
                db.session.add(teacher_role)
                contributor_role = Roles(name="contributor")
                db.session.add(contributor_role)
                user_role = Roles(name="user")
                db.session.add(user_role)
                db.session.commit()

                # Link rights and roles together
                admin_role_rights = []
                for admin_right in admin_rights:
                    right = Rights.query.filter_by(name=admin_right).first()
                    if right is not None:
                        role_right = RoleRights(role_id=admin_role.id, right_id=right.id)
                        admin_role_rights.append(role_right)

                teacher_role_rights = []
                for teacher_right in teacher_rights:
                    right = Rights.query.filter_by(name=teacher_right).first()
                    if right is not None:
                        role_right = RoleRights(role_id=teacher_role.id, right_id=right.id)
                        teacher_role_rights.append(role_right)

                contributor_role_rights = []
                for contributor_right in contributor_rights:
                    right = Rights.query.filter_by(name=contributor_right).first()
                    if right is not None:
                        role_right = RoleRights(role_id=contributor_role.id, right_id=right.id)
                        contributor_role_rights.append(role_right)

                db.session.add_all(admin_role_rights)
                db.session.add_all(teacher_role_rights)
                db.session.add_all(contributor_role_rights)
                db.session.commit()

                # Give rights to the new admin
                rights = []
                role_rights = RoleRights.query.filter_by(role_id=admin_role.id).all()

                for role_right in role_rights:
                    user_rights = UserRights()
                    user_rights.user_id = admin.id
                    user_rights.right_id = role_right.right_id
                    rights.append(user_rights)

                db.session.add_all(rights)
                db.session.commit()


            except IntegrityError:
                db.session.rollback()

            try:
                db.session.add(page)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            login_user(admin)

            db.session.close()
            with app.app_context():
                cache.clear()

            return redirect(url_for("views.static_html"))
        return render_template("setup.html", state=serialize(generate_nonce()))
    return redirect(url_for("views.static_html"))


@views.route("/notifications", methods=["GET"])
def notifications():
    notifications = Notifications.query.order_by(Notifications.id.desc()).all()
    return render_template("notifications.html", notifications=notifications)


@views.route("/settings", methods=["GET"])
@authed_only
def settings():
    infos = get_infos()

    user = get_current_user()
    name = user.name
    email = user.email
    website = user.website
    affiliation = user.affiliation
    country = user.country
    school = user.school

    tokens = UserTokens.query.filter_by(user_id=user.id).all()

    prevent_name_change = get_config("prevent_name_change")

    if get_config("verify_emails") and not user.verified:
        confirm_url = markup(url_for("auth.confirm"))
        infos.append(
            markup(
                "Your email address isn't confirmed!<br>"
                "Please check your email to confirm your email address.<br><br>"
                f'To have the confirmation email resent please <a href="{confirm_url}">click here</a>.'
            )
        )

    return render_template(
        "settings.html",
        name=name,
        email=email,
        website=website,
        affiliation=affiliation,
        country=country,
        school=school,
        tokens=tokens,
        prevent_name_change=prevent_name_change,
        infos=infos,
    )


@views.route("/", defaults={"route": "index"})
@views.route("/<path:route>")
def static_html(route):
    """
    Route in charge of routing users to Pages.
    :param route:
    :return:
    """
    page = get_page(route)
    if page is None:
        abort(404)
    else:
        if page.auth_required and authed() is False:
            return redirect(url_for("auth.login", next=request.full_path))

        return render_template("page.html", content=page.content)


@views.route("/tos")
def tos():
    tos_url = get_config("tos_url")
    tos_text = get_config("tos_text")
    if tos_url:
        return redirect(tos_url)
    elif tos_text:
        return render_template("page.html", content=build_html(tos_text))
    else:
        abort(404)


@views.route("/privacy")
def privacy():
    privacy_url = get_config("privacy_url")
    privacy_text = get_config("privacy_text")
    if privacy_url:
        return redirect(privacy_url)
    elif privacy_text:
        return render_template("page.html", content=build_html(privacy_text))
    else:
        abort(404)


@views.route("/files", defaults={"path": ""})
@views.route("/files/<path:path>")
def files(path):
    """
    Route in charge of dealing with making sure that CTF challenges are only accessible during the competition.
    :param path:
    :return:
    """
    f = Files.query.filter_by(location=path).first_or_404()
    if f.type == "challenge":
        # si les challenges sont visibles
        if challenges_visible() is False:
            # Allow downloads if a valid token is provided
            token = request.args.get("token", "")
            try:
                data = unserialize(token, max_age=3600)
                user_id = data.get("user_id")
                file_id = data.get("file_id")
                user = Users.query.filter_by(id=user_id).first()

                # Check user is admin if challenge_visibility is admins only
                if (
                    get_config(ConfigTypes.CHALLENGE_VISIBILITY) == "admins"
                    and user.type != "admin"
                ):
                    abort(403)

                # Check that the user exists and isn't banned
                if user:
                    if user.banned:
                        abort(403)
                else:
                    abort(403)

                # Check that the token properly refers to the file
                if file_id != f.id:
                    abort(403)

            # The token isn't expired or broken
            except (BadTimeSignature, SignatureExpired, BadSignature):
                abort(403)

    uploader = get_uploader()
    try:
        return uploader.download(f.location)
    except IOError:
        abort(404)


@views.route("/themes/<theme>/static/<path:path>")
def themes(theme, path):
    """
    General static file handler
    :param theme:
    :param path:
    :return:
    """
    for cand_path in (
            safe_join(app.root_path, "themes", cand_theme, "static", path)
            # The `theme` value passed in may not be the configured one, e.g. for
            # admin pages, so we check that first
            for cand_theme in (theme, *config.ctf_theme_candidates())
    ):
        if os.path.isfile(cand_path):
            return send_file(cand_path)
    abort(404)
