
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
import requests
from flask import url_for
from pydantic import ValidationError
from sqlalchemy import select

import app.shared.datetime_.helpers as dth
from app._infra.database import db_session
from app.modules.auth.models import HourCycleEnum, UnitSystemEnum, User, UserRoleEnum
from app.modules.auth.repository import UsersRepository
from app.modules.auth.schemas import UserPatch, UserProfilePatch, UserRegister
from app.modules.auth.service import create_auth_service
from app.modules.groceries.service import create_groceries_service
from app.modules.tasks.models import PriorityEnum
from app.modules.tasks.schemas import TaskCreate
from app.modules.tasks.service import create_tasks_service
from app.shared.exceptions import ServiceError
from app.shared.models import Pillar


@pytest.fixture
def auth_service(logged_in_user):
    return create_auth_service(db_session, user_id=logged_in_user.id)


def test_register_via_form_page(client):
    resp = client.post("/register", data={
        "username": "test_user",
        "password": "password123",
        "name": "Steve",
        "timezone": "America/Chicago",
    })

    assert resp.headers.get("Location") == "/"
    user = db_session.execute(
        select(User).where(User.username=="test_user")
    ).scalar_one_or_none()

    assert user.name == "Steve"


def test_register_via_form_page_no_name(client):
    client.post("/register", data={
        "username": "test_user",
        "password": "password123",
        "name": "",
        "timezone": "America/Chicago",
    })
    user = db_session.execute(
        select(User).where(User.username=="test_user")
    ).scalar_one_or_none()
    assert user.name is None

def test_register_one(auth_service):
    my_user = {
        "username": "steve",
        "password": "password123",
        "name": None,
        "timezone": "America/Chicago",
    }
    validated = UserRegister(**my_user)

    user = auth_service.register_user(validated)
    assert user.id is not None
    assert user.password_hash != "password123"
    assert user.check_password("password123")
    assert user.timezone == "America/Chicago" # TODO: ???

    # pillars
    pillars = db_session.execute(
        select(Pillar).where(Pillar.user_id == user.id)
    ).scalars().all()

    assert len(set(pillars)) == 5

def test_register_duplicate_username_raises_integrity(auth_service):
    user1 = {
        "username": "steve",
        "password": "password123",
        "name": None,
        "timezone": "America/Chicago",
    }
    validated = UserRegister(**user1)
    user2 = {
        "username": "steve",
        "password": "anotherpass",
        "name": "Not steve",
        "timezone": "America/Chicago",
    }
    validated2 = UserRegister(**user2)

    user1 = auth_service.register_user(validated)
    with pytest.raises(ServiceError, match="Username already exists"):
        user2 = auth_service.register_user(validated2)


## ROUTES


# 2. POST /register w valid data, then hit a login-required page with the same client,
# and assert we can get in.
## TODO: Rename
def test_logged_in_after_register(client):
    client.post("/register", data = {
        "username": "steve", "password": "password123", "timezone": "America/Chicago"
    })
    user = db_session.execute(
        select(User).where(User.username=="steve")
    ).scalar_one_or_none()

    assert user is not None
    with client.session_transaction() as session:
        assert "_user_id" in session
        assert session["_user_id"] == str(user.id)

# 3. PATCH /profile/me with a valid body -> 200, and the DB row changed.
#  then with garbage country -> 4xx
# This now fails properly: timezone isn't on UserProfilePatch -> only UserPatch
def test_profile_patch_rejects_unknown_field(authenticated_client):
    resp = authenticated_client.patch("/api/profile/me", json={ "timezone": "America/New_York" })
    assert resp.status_code == 400


# 4. Capture the CRSF token pre-login, login, capture again, and assert they differ.


# 5. Build the app with the prod config and no SECRET_KEY in the env, assert it raises.
# monkeypatch.delenv lets us control the env inside a test


# 6. Either assert the config vals on a prod-config app, or better - make a request and inspect
# the Set-Cookie header for Secure; HttpOnly; SameSite.



# 7. UserRegister(password="1234", ...) raisees.


# 8. Register the same username twice, assert ServiceError with the dupe msg.



### TESTING SCHEMAS STUFF

def test_user_patch_name_only_never_raises():
    validated = UserPatch(name="steve")
    validated_two = UserPatch(name=None)

    assert validated.name == "steve"
    assert validated_two.name is None

def test_user_patch_timezone_none_raises():
    with pytest.raises(ValidationError):
        _ = UserPatch(timezone=None)

def test_user_patch_timezone_invalid_iana():
    with pytest.raises(ValidationError):
        _ = UserPatch(timezone="America/Fake_City")

def test_user_patch_timezone_valid_iana():
    validated = UserPatch(timezone="America/New_York")
    assert validated.timezone == "America/New_York"


@pytest.mark.parametrize("field", ["unit_system", "hour_cycle"])
def test_user_profile_patch_rejects_nulls(field):
    with pytest.raises(ValueError):
        UserProfilePatch(**{field: None})



# TEST: Update paths for: UserPatch, UserProfilePatch, & UserGoalsPatch

def test_users_patch_happy_path(authenticated_client, logged_in_user):
    resp = authenticated_client.patch("/api/users/me", json={"timezone": "Europe/London" })

    assert resp.status_code == 200
    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()

    assert user.timezone == "Europe/London"

@pytest.mark.parametrize("endpoint, payload, read, unchanged", [
    ("/api/users/me", {"timezone": None},       lambda x: x.timezone, "America/Chicago"),
    ("/api/profile/me", {"unit_system": None},  lambda x: x.profile.unit_system, UnitSystemEnum.IMPERIAL),
    ("/api/profile/me", {"hour_cycle": None},   lambda x: x.profile.hour_cycle, HourCycleEnum.H12),
])
def test_patch_explicit_nulls_rejected(authenticated_client, logged_in_user, endpoint, payload, read, unchanged):
    resp = authenticated_client.patch(endpoint, json=payload)

    assert resp.status_code == 400
    user = db_session.execute(select(User).where(User.id==logged_in_user.id)).scalar_one()
    assert read(user) == unchanged


def test_goals_patch(authenticated_client, logged_in_user):
    resp = authenticated_client.patch("/api/goals/me", json={ "calories": 2200 })

    assert resp.status_code == 200
    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()

    assert user.goals.calories == 2200

def test_goals_patch_nulls_clear_target(authenticated_client, logged_in_user):
    authenticated_client.patch("/api/goals/me", json={ "calories": 2200 })
    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()
    assert user.goals.calories == 2200

    authenticated_client.patch("/api/goals/me", json={ "calories": None })
    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()
    assert user.goals.calories is None

# Test the profile/me payload return shape
def test_get_profile_me(authenticated_client):
    resp = authenticated_client.get("/api/profile/me")

    assert resp.status_code == 200
    assert len(resp.json.keys()) == 3
    assert resp.json["timezone"] == "America/Chicago"
    assert resp.json["profile"]["unit_system"] == UnitSystemEnum.IMPERIAL
    assert resp.json["profile"]["hour_cycle"] == HourCycleEnum.H12
    assert resp.json["profile"]["city"] is None
    assert resp.json["profile"]["country"] is None


def test_patch_user_invalid_timezone(authenticated_client):
    resp = authenticated_client.patch("/api/users/me", json={ "timezone": "Not/Real" })

    assert resp.status_code == 400


@pytest.fixture
def geocode_mock(monkeypatch):
    mock = SimpleNamespace(
        calls=[],
        results=[{"name": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278}],
        exc=None,
    )

    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return mock.results

    def fake_get(url, params, timeout):
        if mock.exc:
            raise mock.exc
        mock.calls.append(params["q"])
        return FakeResp()

    monkeypatch.setattr("app.modules.auth.service.requests.get", fake_get)
    return mock

## Set both city and country to none -> ensure geocode doesnt call with "None,None" query
def test_thing(auth_service, logged_in_user, geocode_mock):
    patch = UserProfilePatch(city=None, country=None)
    # with pytest.raises(ServiceError, match="State is only valid for US locations"):
    auth_service.update_profile(patch, logged_in_user.id)

    assert geocode_mock.calls == [] # raise catches before external call
    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()
    assert user.profile.latitude is None
    assert user.profile.longitude is None



## Sent: city + country (valid) -> Ensure city/country/lat/lon go all together
def test_location_all_or_none(auth_service, logged_in_user, geocode_mock):
    # Wire into update_profile s.t. city/country ALSO patches lat/lon
    # If they aren't updated together, our DB constraint should fire
    patch = UserProfilePatch(city="london", country="GB")
    auth_service.update_profile(patch, logged_in_user.id)

    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()

    # So, ALL four need to be set. Need to ensure that lat/lon are also set here?
    assert geocode_mock.calls == ["london,GB"]
    assert user.profile.city == "London"
    assert user.profile.country == "GB"
    assert user.profile.latitude is not None
    assert user.profile.longitude is not None
    assert user.profile.latitude == 51.5074
    assert user.profile.longitude == -0.1278

## Sent: state but country isn't US -> Raises before call
def test_state_present_country_not_us_raises(auth_service, logged_in_user, geocode_mock):
    patch = UserProfilePatch(city="London", state="MI", country="GB")
    with pytest.raises(ServiceError, match="State is only valid for US locations"):
        auth_service.update_profile(patch, logged_in_user.id)

    assert geocode_mock.calls == [] # raise catches before external call
    # Other: city+country=US, no state -> 200 also valid
    patch = UserProfilePatch(city="Miami", country="US")
    auth_service.update_profile(patch, logged_in_user.id)
    assert True


## Sent: invalid city + country combo -> Raises: geocoder returned no results
def test_invalid_geocode_query_no_results(auth_service, logged_in_user, geocode_mock):
    # Scene: geocoder finds nothing:
    geocode_mock.results = []

    patch = UserProfilePatch(city="Paris", country="GB")
    with pytest.raises(ServiceError, match="Could not resolve that location"):
        auth_service.update_profile(patch, logged_in_user.id)

    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()

    assert geocode_mock.calls == ["Paris,GB"]
    assert user.profile.city is None
    assert user.profile.country is None
    # Do we need to assert lat/lon unchanged? if these are none, we should hit DB constraint
    #  anyway.


## Sent: No location-related changes -> No geocode calls
def test_no_location_change_does_not_call_geocode(auth_service, logged_in_user, geocode_mock):
    patch = UserProfilePatch(unit_system=UnitSystemEnum.METRIC)
    auth_service.update_profile(patch, logged_in_user.id)

    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()

    assert geocode_mock.calls == []
    assert user.profile.unit_system == UnitSystemEnum.METRIC


# set unit and city valid -> ensure city sets canonical name AND units are changed
def test_mixed(auth_service, logged_in_user, geocode_mock):
    patch = UserProfilePatch(unit_system=UnitSystemEnum.METRIC, city="london", country="GB")
    auth_service.update_profile(patch, logged_in_user.id)

    user = db_session.execute(
        select(User).where(User.id==logged_in_user.id)
    ).scalar_one()

    assert geocode_mock.calls == ["london,GB"] # lowercase 'london' in query
    assert user.profile.unit_system == UnitSystemEnum.METRIC
    assert user.profile.city == "London" # capital 'London' from response gets stored
    assert user.profile.country == "GB"


## Sent city only against empty profile -> 400, calls = []
def test_city_only_empty_profile_400s(auth_service, logged_in_user, geocode_mock):
    patch = UserProfilePatch(city="london")
    with pytest.raises(ServiceError, match="Both city and country required"):
        auth_service.update_profile(patch, logged_in_user.id)

    assert geocode_mock.calls == []


def test_api_down(auth_service, logged_in_user, geocode_mock):
    geocode_mock.exc = requests.RequestException()
    patch = UserProfilePatch(city="london", country="GB")
    with pytest.raises(ServiceError, match="Location service unavailable"):
        auth_service.update_profile(patch, logged_in_user.id)

    assert geocode_mock.calls == []

def test_goals_bounds_rejection(authenticated_client):
    resp = authenticated_client.patch("/api/goals/me", json={"weight": 0})

    assert resp.status_code == 400



def test_user_macros_summary(logged_in_user):
    # Build user with goals set
    user = db_session.execute(select(User).where(User.id==logged_in_user.id)).scalar_one()

    user.goals.weight=70
    user.goals.calories=75
    user.goals.steps=80
    user.goals.sleep_duration_minutes=90
    user.goals.protein_pct=25
    user.goals.fat_pct=30
    user.goals.carbs_pct=45
    db_session.flush()

    # Call macros_summary
    groceries_service = create_groceries_service(db_session, logged_in_user.id, user.timezone)
    start_utc, end_utc = dth.last_n_days_range(days_ago=5, tz_str=user.timezone)
    result, _ = groceries_service.macros_summary(start_utc, end_utc)

    # Assert targets in output
    assert result["calories"]["target"] == 75
    assert result["protein"]["target"] == 25
    assert result["fat"]["target"] == 30
    assert result["carbs"]["target"] == 45
    assert set(result) == {"calories", "protein", "carbs", "fat"}




### TODO: Drafting the unusable password / demo-fixing stuff
# Note: wanna add to our UserRole enum to include DEMO for easy "DELETE demo users older than N days"
# use DEMO role to guard for geocode too

def test_unusable_password_rejects_all_input(session, logged_in_user):
    # user = session.get(User, logged_in_user.id)
    # create user with unusable password:
    user = User(username="demo")
    user.set_unusable_password()
    assert not user.check_password("fff")
    assert not user.check_password("")

def test_normal_password_still_authenticates():
    user = User(username="real")
    user.hash_password("password1234")
    assert user.check_password("password1234")
    assert not user.check_password("incorrect")

# --- create_demo_user ---

def test_create_demo_user(auth_service, session):
    user = auth_service.create_demo_user()
    session.flush()

    assert user.role == UserRoleEnum.DEMO
    assert not user.check_password("anything")        # unusable password shut the login door
    assert user.username.startswith("demo_")
    assert user.profile is not None
    assert user.goals is not None

    pillars = session.scalars(select(Pillar).where(Pillar.user_id == user.id)).all()
    assert len(pillars) == 5


def test_create_demo_user_is_unique_per_call(auth_service, session):
    u1 = auth_service.create_demo_user()
    u2 = auth_service.create_demo_user()
    session.flush()
    assert u1.username != u2.username                 # not a shared singleton


# --- reaper ---

def test_reap_skips_recent_demo_user(auth_service, session):
    user = auth_service.create_demo_user()
    session.flush()

    count = UsersRepository(session).delete_stale_demo_users(
        datetime.now(timezone.utc) - timedelta(days=1)   # cutoff in the past
    )
    assert count == 0
    assert session.get(User, user.id) is not None


def test_reap_deletes_stale_demo_user(auth_service, session):
    user = auth_service.create_demo_user()
    session.flush()
    uid = user.id

    count = UsersRepository(session).delete_stale_demo_users(
        datetime.now(timezone.utc) + timedelta(days=1)   # cutoff in the future
    )
    assert count == 1
    assert session.get(User, uid) is None


def test_reap_never_touches_non_demo_users(session, logged_in_user):
    count = UsersRepository(session).delete_stale_demo_users(
        datetime.now(timezone.utc) + timedelta(days=1)
    )
    assert count == 0                                  # role guard, not just the date
    assert session.get(User, logged_in_user.id) is not None


def test_reap_cascades_demo_user_data(auth_service, session):
    user = auth_service.create_demo_user()             # seeds pillars + demo data
    session.flush()
    uid = user.id

    UsersRepository(session).delete_stale_demo_users(   # must not raise under lazy="raise"
        datetime.now(timezone.utc) + timedelta(days=1)
    )
    session.flush()

    pillars = session.scalars(select(Pillar).where(Pillar.user_id == uid)).all()
    assert pillars == []                               # DB cascade fired for child rows


# --- route ---

def test_init_demo_logs_in_fresh_demo_user(client):
    resp = client.post("/init-demo")
    assert resp.headers.get("Location") == "/"

    with client.session_transaction() as sess:
        uid = sess.get("_user_id")
    assert uid is not None
    assert db_session.get(User, int(uid)).role == UserRoleEnum.DEMO


def test_init_demo_swaps_out_authenticated_user(authenticated_client, logged_in_user):
    authenticated_client.post("/init-demo")

    with authenticated_client.session_transaction() as sess:
        uid = sess.get("_user_id")
    assert uid is not None
    assert uid != str(logged_in_user.id)               # route logged the old user out first
    assert db_session.get(User, int(uid)).role == UserRoleEnum.DEMO


@pytest.fixture
def tasks_service(logged_in_user):
    return create_tasks_service(db_session, logged_in_user.id, logged_in_user.timezone)

## Ensure User A can't GET/PATCH/DELETE user B's entities
def test_entities_scoper_per_user(logged_in_user, second_logged_in_user, tasks_service, session):
    # Add task for user A
    validated = TaskCreate(name="test", priority=PriorityEnum.LOW)
    t = tasks_service.create_task(validated)

    service_b = create_tasks_service(session, second_logged_in_user.id, second_logged_in_user.timezone)
    with pytest.raises(ServiceError, match="Task not found"):
        service_b.get_task(t.id)


def test_all_api_endpoints_reject_unauthenticated(app, client):
    public = {"api.get_weather"} # explicit allowlist

    # app.url_map.iter_rules() gives every registered rule with its methods
    failures = []
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if not rule.rule.startswith("/api") or rule.endpoint in public:
                continue
            url = url_for(rule.endpoint, **dict.fromkeys(rule.arguments, 1))
            for method in rule.methods - {"HEAD", "OPTIONS"}:
                resp = client.open(url, method=method, json={})
                if resp.status_code != 401:
                    failures.append(f"{method} {url} -> {resp.status_code}")

    assert not failures, "\n".join(failures)
