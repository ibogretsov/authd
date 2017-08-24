import pytest
import random


@pytest.fixture
def rnd_gen():
    return random.Random(123456)


@pytest.fixture
def rnd(rnd_gen):
    return rnd_gen.random()
