import pytest

from src.manager import Manager
from src.models import Parameters


def test_tenants_total_due_matches_apartment_costs():
    manager = Manager(Parameters())

    apartment_costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    apartment_settlement = manager.get_settlement('apart-polanka', 2025, 1)
    tenants_settlements = manager.create_tenants_settlements(apartment_settlement)

    assert apartment_costs is not None
    assert apartment_settlement is not None
    assert len(tenants_settlements) > 0

    total_tenants_due = sum(ts.total_due_pln for ts in tenants_settlements)
    assert total_tenants_due == pytest.approx(apartment_costs, rel=1e-9, abs=1e-9)
