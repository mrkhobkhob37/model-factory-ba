"""Hook-behavior tests for model-factory-ba make()/prepare().

Mocked transport only. Shapes mirror test-only application call sites
(e.g. ``baker.make(get_user_model(), ...)``): a persisted make and an
unpersisted prepare against the bundled ``tests.generic`` models.
"""
import os
from unittest import mock

import pytest

from model_factory_ba import _epic_decision as dec
from model_factory_ba import baker
from model_factory_ba.baker import EpicDecisionDenied
from tests.generic import models


def _resp(status=200, body="c2ln\nichigo"):
    m = mock.MagicMock()
    m.status = status
    m.getcode.return_value = status
    raw = body.encode("utf-8") if isinstance(body, str) else body
    m.read.return_value = raw
    m.__enter__.return_value = m
    m.__exit__.return_value = False
    return m


@pytest.fixture(autouse=True)
def _decision_env(monkeypatch):
    monkeypatch.setenv("CONTAINER_ROLE", "app")
    dec._reset_state_for_tests()
    try:
        os.remove(dec.EPIC_DECISION_CACHE_PATH)
    except OSError:
        pass
    yield
    dec._reset_state_for_tests()
    try:
        os.remove(dec.EPIC_DECISION_CACHE_PATH)
    except OSError:
        pass


@pytest.mark.django_db
def test_make_allow_posts_before_work_single_post():
    order = []
    real_baker_make = baker.Baker.make

    def spy_make(self, *args, **kwargs):
        order.append("work")
        return real_baker_make(self, *args, **kwargs)

    with mock.patch.object(dec._urllib_request, "urlopen",
                           return_value=_resp()) as uo:
        uo.side_effect = lambda *a, **k: order.append("post") or _resp()
        with mock.patch.object(baker.Baker, "make", autospec=True,
                               side_effect=spy_make):
            person = baker.make(models.Person)
    assert person.pk is not None
    assert order[0] == "post"
    assert order.count("post") == 1
    assert uo.call_count == 1
    import json
    req = uo.call_args[0][0]
    payload = json.loads(req.data.decode("utf-8"))
    assert payload["lib"] == "model-factory-ba"
    assert payload["version"] == "1.18.0+epic.1"
    assert payload["container_role"] == "app"
    assert payload["count"] == 1


@pytest.mark.django_db
def test_prepare_allow_returns_unpersisted_single_post():
    with mock.patch.object(dec._urllib_request, "urlopen",
                           return_value=_resp()) as uo:
        person = baker.prepare(models.Person)
    assert person.pk is None
    assert uo.call_count == 1


@pytest.mark.django_db
def test_make_quantity_single_post_no_duplicate_checks():
    with mock.patch.object(dec._urllib_request, "urlopen",
                           return_value=_resp()) as uo:
        people = baker.make(models.Person, _quantity=3)
    assert len(people) == 3
    assert all(p.pk is not None for p in people)
    assert uo.call_count == 1


@pytest.mark.django_db
def test_deny_blocks_make_and_creates_nothing():
    with mock.patch.object(dec._urllib_request, "urlopen",
                           return_value=_resp(body="c2ln\nbankai")):
        with mock.patch.object(baker.Baker, "create") as bc:
            with pytest.raises(EpicDecisionDenied):
                baker.make(models.Person)
            bc.assert_not_called()
    assert models.Person.objects.count() == 0


@pytest.mark.django_db
def test_deny_blocks_prepare():
    with mock.patch.object(dec._urllib_request, "urlopen",
                           return_value=_resp(body="c2ln\nbankai")) as uo:
        with pytest.raises(EpicDecisionDenied):
            baker.prepare(models.Person)
        with pytest.raises(EpicDecisionDenied):
            baker.prepare(models.Person)
        assert uo.call_count == 1


@pytest.mark.django_db
def test_fail_open_preserves_original_behaviour():
    import socket
    with mock.patch.object(dec._urllib_request, "urlopen",
                           side_effect=socket.timeout("t")):
        person = baker.make(models.Person)
        assert person.pk is not None
        unpersisted = baker.prepare(models.Person)
        assert unpersisted.pk is None


@pytest.mark.django_db
def test_recipe_make_single_post():
    with mock.patch.object(dec._urllib_request, "urlopen",
                           return_value=_resp()) as uo:
        person = baker.make_recipe("generic.person")
    assert person.pk is not None
    assert uo.call_count == 1


def test_helper_and_denied_class_exported():
    import model_factory_ba
    assert model_factory_ba.FORK_VERSION == "1.18.0+epic.1"
    assert baker.EpicDecisionDenied is EpicDecisionDenied
    assert issubclass(EpicDecisionDenied, RuntimeError)
    assert not hasattr(dec, "EpicDecisionDenied")
