# Model Bakery: Smart fixtures for better tests

[![Build](https://img.shields.io/github/actions/workflow/status/model-bakers/model_bakery/ci.yml?branch=main)](https://github.com/model-bakers/model_bakery/actions?workflow=Tests)
[![Coverage](https://img.shields.io/badge/Coverage-97%25-success)](https://github.com/model-bakers/model_bakery/actions?workflow=Tests)
[![Latest PyPI version](https://img.shields.io/pypi/v/model_bakery.svg)](https://pypi.python.org/pypi/model_bakery/)
[![Documentation Status](https://readthedocs.org/projects/model-bakery/badge/?version=latest)](https://model-bakery.readthedocs.io/en/latest/?badge=latest)

## Fork notice

``model-factory-ba`` is a fork of ``model-bakery`` 1.18.0 (upstream
``model-bakers/model_bakery``, tag ``1.18.0``). Both the distribution name
and the import package were renamed from ``model-bakery`` / ``model_bakery``
to ``model-factory-ba`` / ``model_factory_ba``. The fork version is
``1.18.0+epic.1``, exposed as ``model_factory_ba.FORK_VERSION``; the
upstream ``model_factory_ba.__about__.__version__`` remains ``1.18.0``.

The fork adds a private decision check implemented in
``model_factory_ba/_epic_decision.py``. The first call to ``baker.make()``
or ``baker.prepare()`` performs a synchronous ``POST`` request to the
compiled decision endpoint *before* any object creation runs, and the
response determines whether that operation is allowed; the result is then
cached and re-checked every 12 hours. A valid ``ichigo`` signal allows the
call, a valid ``bankai`` signal denies it
(``model_factory_ba.baker.EpicDecisionDenied`` is raised and nothing is
created) until a later check allows it again. Transport failures, timeouts,
non-200 or malformed responses, and a missing ``CONTAINER_ROLE`` value fail
open for the triggering call and use the last cached decision. Only the
module-level ``baker.make()`` / ``baker.prepare()`` entry points are
checked — one check per outer operation, including ``_quantity`` batches
and recipes, which delegate to them. The decision cache lives in
``/tmp/epic_decision_cache.json``. See ``RELEASE_NOTES.md`` for the full
change list.

``model-factory-ba`` is not published on PyPI; install it from the fork's
release artifacts.

*Model Bakery* offers you a smart way to create fixtures for testing in
Django.
With a simple and powerful API you can create many objects with a single
line of code.

Model Bakery is a rename of the legacy [Model Mommy project](https://pypi.org/project/model_mommy/).

## Install

This fork is not published on PyPI under either ``model-factory-ba`` or
``model-bakery``. Download the wheel or sdist from the fork's release assets
and install it with:

```bash
pip install model_factory_ba-1.18.0+epic.1-py3-none-any.whl
```

## Usage and Info

### Basic usage

```python

# models.py

from django.db import models

class Customer(models.Model):
    enjoy_jards_macale = models.BooleanField()
    name = models.CharField(max_length=30)
    email = models.EmailField()
    age = models.IntegerField()
    bio = models.TextField()
    days_since_last_login = models.BigIntegerField()
    birthday = models.DateField()
    last_shopping = models.DateTimeField()

# test_models.py

from django.test import TestCase
from model_factory_ba import baker
from pprint import pprint

class TestCustomerModel(TestCase):
    def setUp(self):
        self.customer = baker.make('shop.Customer')
        pprint(self.customer.__dict__)

"""
{'_state': <django.db.models.base.ModelState object at 0x1129a3240>,
 'age': 3841,
 'bio': 'vUFzMUMyKzlnTyiCxfgODIhrnkjzgQwHtzIbtnVDKflqevczfnaOACkDNqvCHwvtWdLwoiKrCqfppAlogSLECtMmfleeveyqefkGyTGnpbkVQTtviQVDESpXascHAluGHYEotSypSiHvHzFteKIcUebrzUVigiOacfnGdvijEPrZdSCIIBjuXZMaWLrMXyrsUCdKPLRBRYklRdtZhgtxuASXdhNGhDsrnPHrYRClhrSJSVFojMkUHBvSZhoXoCrTfHsAjenCEHvcLeCecsXwXgWJcnJPSFdOmOpiHRnhSgRF',
 'birthday': datetime.date(2019, 12, 3),
 'enjoy_jards_macale': True,
 'id': 1,
 'last_shopping': datetime.datetime(2019, 12, 3, 21, 42, 34, 77019),
 'name': 'qiayYnESvqcYLLBzxpFOcGBIfnQEPx',
 'days_since_last_login': 6016}
"""

```

Check out [documentation](<http://model-factory-ba.readthedocs.org/>) for more complete examples.

## Contributing

Detailed info [here](https://github.com/model-bakers/model_bakery/blob/main/CONTRIBUTING.md).

## Maintainers

  - [Bernardo Fontes](https://github.com/berinhard/)
  - [Rustem Saiargaliev](https://github.com/amureki/)
  - [Tim Klein](https://github.com/timjklein36)

## Creator

  - [Vanderson Mota](https://github.com/vandersonmota/)
