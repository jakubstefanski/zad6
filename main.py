import sys
from pathlib import Path

from src.manager import Manager
from src.models import Parameters


def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_subsection_header(title: str):
    """Print a formatted subsection header"""
    print(f"\n  {title}")
    print(f"  {'-' * 40}")


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{amount:,.2f} PLN"


def display_apartments(manager):
    """Display all apartments with their rooms and bills"""
    print_section_header("APARTMENTS")
    
    for apartment in manager.apartments.values():
        print(f"\n {apartment.name} ({apartment.key})")
        print(f"   Location: {apartment.location}")
        print(f"   Total Area: {apartment.area_m2} m²")
        
        print_subsection_header("Rooms")
        for room in apartment.rooms.values():
            print(f"{room.name:<25} {room.area_m2:>6} m²")
        
        # Find bills for this apartment
        apartment_bills = [bill for bill in manager.bills if bill.apartment == apartment.key]
        if apartment_bills:
            print_subsection_header("Bills")
            for bill in apartment_bills:
                month_year = f"{bill.settlement_month}/{bill.settlement_year}" if bill.settlement_month and bill.settlement_year else "N/A"
                print(f"      • {bill.type:<15} {format_currency(bill.amount_pln):>15}  Due: {bill.date_due}  Period: {month_year}")


def display_tenants(manager):
    """Display all tenants with their details and transfers"""
    print_section_header("TENANTS")
    
    for tenant in manager.tenants.values():
        print(f"\n {tenant.name}")
        print(f"   Apartment: {tenant.apartment}")
        print(f"   Room: {tenant.room}")
        print(f"   Rent: {format_currency(tenant.rent_pln)}/month")
        print(f"   Deposit: {format_currency(tenant.deposit_pln)}")
        print(f"   Agreement: {tenant.date_agreement_from} to {tenant.date_agreement_to}")
        
        # Find transfers for this tenant
        tenant_transfers = [transfer for transfer in manager.transfers if transfer.tenant == tenant.name]
        if tenant_transfers:
            print_subsection_header("Transfers")
            for transfer in tenant_transfers:
                month_year = f"{transfer.settlement_month}/{transfer.settlement_year}" if transfer.settlement_month and transfer.settlement_year else "N/A"
                print(f"      • {format_currency(transfer.amount_pln):>15}  Date: {transfer.date}  Period: {month_year}")


def display_settlement(manager: Manager, apartment_key: str, year: int, month: int) -> bool:
    """Display settlement for a specific apartment, year, and month."""
    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    if apartment_settlement is None:
        print(f"Error: Apartment '{apartment_key}' not found.")
        print(f"Available apartments: {', '.join(manager.apartments.keys())}")
        return False

    apartment = manager.apartments[apartment_key]
    tenants_settlements = manager.create_tenants_settlements(apartment_settlement)

    print_section_header(f"SETTLEMENT: {apartment.name} ({apartment_settlement.key})")
    print(f"   Apartment: {apartment.key}")
    print(f"   Period: {month}/{year}")
    print(f"   Total Due: {format_currency(apartment_settlement.total_due_pln)}")

    period_bills = [
        bill for bill in manager.bills
        if bill.apartment == apartment_key
        and bill.settlement_year == year
        and bill.settlement_month == month
    ]
    print_subsection_header("Bills")
    if period_bills:
        for bill in period_bills:
            print(f"      - {bill.type:<15} {format_currency(bill.amount_pln):>15}  Due: {bill.date_due}")
    else:
        print("      No bills for this period.")

    print_subsection_header("Tenants Settlements")
    if tenants_settlements:
        for tenant_settlement in tenants_settlements:
            print(f"      - {tenant_settlement.tenant:<25} {format_currency(tenant_settlement.total_due_pln):>15}")
        total_tenants_due = sum(ts.total_due_pln for ts in tenants_settlements)
        print(f"      {'-' * 42}")
        print(f"      {'Total':<25} {format_currency(total_tenants_due):>15}")
    else:
        print("      No tenants assigned to this apartment.")

    return True


if __name__ == '__main__':
    parameters = Parameters()
    manager = Manager(parameters)

    if len(sys.argv) == 1:
        display_apartments(manager)
        display_tenants(manager)
    elif len(sys.argv) == 4:
        apartment_key = sys.argv[1]
        try:
            year = int(sys.argv[2])
            month = int(sys.argv[3])
        except ValueError:
            print("Error: Year and month must be integers.")
            print("Usage: python main.py <apartment_key> <year> <month>")
            sys.exit(1)

        try:
            success = display_settlement(manager, apartment_key, year, month)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        if not success:
            sys.exit(1)
    else:
        print("Usage: python main.py [<apartment_key> <year> <month>]")
        print("Example: python main.py apart-polanka 2025 1")
        sys.exit(1)

    print(f"\n{'=' * 70}\n")