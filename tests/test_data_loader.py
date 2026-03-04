"""Tests for data loading and cleaning."""

import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.data_loader import load_ab_data, load_countries, clean_ab_data

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@pytest.fixture(scope="module")
def raw_data():
    return load_ab_data(os.path.join(DATA_DIR, "ab_data.csv"))


@pytest.fixture(scope="module")
def countries():
    return load_countries(os.path.join(DATA_DIR, "countries.csv"))


@pytest.fixture(scope="module")
def clean_data(raw_data, countries):
    return clean_ab_data(raw_data, countries)


class TestLoadData:
    def test_ab_data_loads(self, raw_data):
        assert isinstance(raw_data, pd.DataFrame)
        assert len(raw_data) > 200000

    def test_has_required_columns(self, raw_data):
        required = {"user_id", "timestamp", "group", "landing_page", "converted"}
        assert required <= set(raw_data.columns)

    def test_countries_load(self, countries):
        assert "user_id" in countries.columns
        assert "country" in countries.columns


class TestCleanData:
    def test_fewer_rows_than_raw(self, raw_data, clean_data):
        assert len(clean_data) < len(raw_data)

    def test_no_duplicate_users(self, clean_data):
        assert clean_data["user_id"].is_unique

    def test_has_country_column(self, clean_data):
        assert "country" in clean_data.columns

    def test_groups_match_pages(self, clean_data):
        ctrl = clean_data[clean_data["group"] == "control"]
        treat = clean_data[clean_data["group"] == "treatment"]
        assert (ctrl["landing_page"] == "old_page").all()
        assert (treat["landing_page"] == "new_page").all()

    def test_timestamp_is_datetime(self, clean_data):
        assert pd.api.types.is_datetime64_any_dtype(clean_data["timestamp"])
