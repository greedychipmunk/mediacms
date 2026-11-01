import uuid

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from files.tests import create_account
from users.models import PortalUserSettings, User, user_registration_enabled

PASSWORD = "api_pass_9876"
STRONG_PASSWORD = "Zq8!wvLm3#pT"


def make_user(prefix, **kwargs):
    token = uuid.uuid4().hex[:10]
    return create_account(username=f"{prefix}_{token}", email=f"{prefix}_{token}@example.com", password=PASSWORD, **kwargs)


def signup_payload():
    token = uuid.uuid4().hex[:10]
    return {
        "username": f"signup_{token}",
        "email": f"signup_{token}@example.com",
        "password1": STRONG_PASSWORD,
        "name": "Signed Up Person",
    }


def user_payload():
    token = uuid.uuid4().hex[:10]
    return {
        "username": f"created_{token}",
        "email": f"created_{token}@example.com",
        "name": "Created User",
        "password": STRONG_PASSWORD,
    }


def disable_registration():
    portal_settings = PortalUserSettings.get_solo()
    portal_settings.user_registration_enabled = False
    portal_settings.save()


class RegistrationToggleApiTest(TestCase):
    """The admin-only API to enable/disable self-registration."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = make_user("admin", is_superuser=True)
        cls.manager = make_user("manager", is_manager=True)
        cls.editor = make_user("editor", is_editor=True)
        cls.plain = make_user("plain")

    def setUp(self):
        self.client = APIClient()

    def test_registration_enabled_by_default(self):
        self.assertTrue(user_registration_enabled())

    def test_admin_can_read_registration_state(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/v1/registration")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"enabled": True})

    def test_admin_can_disable_and_enable_registration(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/v1/registration", {"enabled": False}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"enabled": False})
        self.assertFalse(user_registration_enabled())

        response = self.client.post("/api/v1/registration", {"enabled": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"enabled": True})
        self.assertTrue(user_registration_enabled())

    def test_toggle_records_who_changed_it(self):
        self.client.force_authenticate(self.admin)
        self.client.post("/api/v1/registration", {"enabled": False}, format="json")
        self.assertEqual(PortalUserSettings.get_solo().updated_by, self.admin)

    def test_invalid_value_is_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/v1/registration", {"enabled": "maybe"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(user_registration_enabled())

    def test_non_admins_cannot_change_registration(self):
        for user in (self.manager, self.editor, self.plain):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user)
                response = self.client.post("/api/v1/registration", {"enabled": False}, format="json")
                self.assertEqual(response.status_code, 403)
                self.assertTrue(user_registration_enabled())

    def test_non_admins_cannot_read_registration(self):
        for user in (self.manager, self.editor, self.plain):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user)
                self.assertEqual(self.client.get("/api/v1/registration").status_code, 403)

    def test_anonymous_cannot_change_registration(self):
        response = self.client.post("/api/v1/registration", {"enabled": False}, format="json")
        self.assertIn(response.status_code, (401, 403))
        self.assertTrue(user_registration_enabled())


class SignupGateTest(TestCase):
    """Self-registration is blocked while the toggle is off."""

    def test_signup_works_while_registration_enabled(self):
        payload = signup_payload()
        response = self.client.post("/accounts/signup/", payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=payload["username"]).exists())

    def test_signup_blocked_while_registration_disabled(self):
        disable_registration()
        payload = signup_payload()
        response = self.client.post("/accounts/signup/", payload)
        self.assertFalse(User.objects.filter(username=payload["username"]).exists())
        self.assertTemplateUsed(response, "account/signup_closed.html")

    def test_signup_page_shows_closed_page_when_disabled(self):
        disable_registration()
        response = self.client.get("/accounts/signup/")
        self.assertTemplateUsed(response, "account/signup_closed.html")

    def test_signup_works_again_after_registration_is_re_enabled(self):
        disable_registration()
        portal_settings = PortalUserSettings.get_solo()
        portal_settings.user_registration_enabled = True
        portal_settings.save()
        payload = signup_payload()
        response = self.client.post("/accounts/signup/", payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=payload["username"]).exists())

    @override_settings(USERS_CAN_SELF_REGISTER=False)
    def test_static_setting_still_blocks_signup_even_with_toggle_enabled(self):
        payload = signup_payload()
        self.client.post("/accounts/signup/", payload)
        self.assertFalse(User.objects.filter(username=payload["username"]).exists())


class RegisterButtonTest(TestCase):
    """The register button follows the runtime toggle."""

    def test_button_visible_by_default(self):
        response = self.client.get("/")
        self.assertContains(response, "hideRegister: false")

    def test_button_hidden_while_registration_disabled(self):
        admin = make_user("admin", is_superuser=True)
        api_client = APIClient()
        api_client.force_authenticate(admin)
        response = api_client.post("/api/v1/registration", {"enabled": False}, format="json")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/")
        self.assertContains(response, "hideRegister: true")

    def test_button_visible_again_after_registration_is_re_enabled(self):
        disable_registration()
        admin = make_user("admin", is_superuser=True)
        api_client = APIClient()
        api_client.force_authenticate(admin)
        api_client.post("/api/v1/registration", {"enabled": True}, format="json")

        response = self.client.get("/")
        self.assertContains(response, "hideRegister: false")


class CacheInvalidationTest(TestCase):
    """Toggling invalidates the cached value immediately."""

    def test_save_invalidates_cache(self):
        # prime the cache with the default value
        self.assertTrue(user_registration_enabled())
        disable_registration()
        self.assertFalse(user_registration_enabled())


class UserCreationWhileRegistrationDisabledTest(TestCase):
    """Managers and admins can create users no matter the registration toggle."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = make_user("admin", is_superuser=True)
        cls.manager = make_user("manager", is_manager=True)
        cls.editor = make_user("editor", is_editor=True)

    def setUp(self):
        self.client = APIClient()
        disable_registration()

    def test_manager_can_create_user_while_registration_disabled(self):
        self.client.force_authenticate(self.manager)
        payload = user_payload()
        response = self.client.post("/api/v1/users", payload, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username=payload["username"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_admin_can_create_user_while_registration_disabled(self):
        self.client.force_authenticate(self.admin)
        payload = user_payload()
        response = self.client.post("/api/v1/users", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username=payload["username"]).exists())

    def test_editor_cannot_create_users(self):
        self.client.force_authenticate(self.editor)
        response = self.client.post("/api/v1/users", user_payload(), format="json")
        self.assertEqual(response.status_code, 403)


class AdminAddUserTest(TestCase):
    """The Django admin add-user form sets a usable password."""

    def setUp(self):
        self.admin = make_user("admin", is_superuser=True)
        self.client.force_login(self.admin)

    def test_add_user_page_renders_password_fields(self):
        response = self.client.get("/admin/users/user/add/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "password1")
        self.assertContains(response, "password2")

    def test_admin_can_add_user_with_password(self):
        token = uuid.uuid4().hex[:10]
        username = f"admincreated_{token}"
        response = self.client.post(
            "/admin/users/user/add/",
            {
                "username": username,
                "email": f"{username}@example.com",
                "name": "Admin Created",
                "password1": STRONG_PASSWORD,
                "password2": STRONG_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username=username)
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password(STRONG_PASSWORD))
