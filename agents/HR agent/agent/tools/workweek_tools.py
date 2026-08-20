"""WorkWeek (HCM) tools for the HR agent."""
from typing import Dict, Any, Optional
from mocks import workweek_mock

def retrieve_employee_profile(employee_id: str) -> Dict[str, Any]:
    """Retrieve the employee profile and contact details.

    Args:
        employee_id: The unique ID of the employee, e.g., 'EMP001'.

    Returns:
        A dictionary containing the profile details (name, email, department, role, manager, hire_date, address, phone)
        or an error message if not found.
    """
    profile = workweek_mock.retrieve_employee_profile(employee_id)
    if not profile:
        return {"error": f"Employee with ID {employee_id} not found."}
    return profile


def update_contact_info(
    employee_id: str, new_address: Optional[str] = None, new_phone: Optional[str] = None
) -> Dict[str, Any]:
    """Update contact address and/or phone number in the employee's profile.

    Args:
        employee_id: The unique ID of the employee, e.g., 'EMP001'.
        new_address: Optional new home address.
        new_phone: Optional new phone number in E.164 format (e.g. +6591234567).

    Returns:
        A dictionary with 'success' (bool) and optionally 'error' message if validation fails.
    """
    if not new_address and not new_phone:
        return {"success": False, "error": "Must provide at least one of new_address or new_phone to update."}
    return workweek_mock.update_contact_info(employee_id, new_address=new_address, new_phone=new_phone)


def query_time_off_balances(employee_id: str) -> Dict[str, Any]:
    """Query the accrued, used, and remaining time-off leave balances (vacation and sick) for an employee.

    Args:
        employee_id: The unique ID of the employee, e.g., 'EMP001'.

    Returns:
        A dictionary containing vacation and sick balances, or an error message if employee not found.
    """
    balances = workweek_mock.query_time_off_balances(employee_id)
    if not balances:
        return {"error": f"Employee with ID {employee_id} not found."}
    return balances


def submit_leave_request(
    employee_id: str, start_date: str, end_date: str, leave_type: str, work_days: int
) -> Dict[str, Any]:
    """Submit a request for leave (vacation or sick leave).

    Args:
        employee_id: The unique ID of the employee submitting the request, e.g., 'EMP001'.
        start_date: Start date of leave in ISO format 'YYYY-MM-DD' (e.g., '2026-09-01').
        end_date: End date of leave in ISO format 'YYYY-MM-DD' (e.g., '2026-09-05').
        leave_type: The type of leave, either 'vacation' or 'sick'.
        work_days: The number of working days covered by the leave.

    Returns:
        A dictionary containing the transaction result (success, request_id, status) or error message.
    """
    return workweek_mock.submit_leave_request(
        employee_id, start_date_str=start_date, end_date_str=end_date, leave_type=leave_type, work_days=work_days
    )
