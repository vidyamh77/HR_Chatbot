"""WorkWeek (HCM) API Mock Service."""
import re
import datetime
from typing import Dict, Any, Optional

# Mock in-memory database
MOCK_EMPLOYEE_DB: Dict[str, Dict[str, Any]] = {
    "EMP001": {
        "employee_id": "EMP001",
        "name": "Jane Doe",
        "email": "jane.doe@altostrat.com",
        "department": "Engineering",
        "role": "Software Engineer",
        "manager": "EMP003",
        "hire_date": "2022-03-15",
        "address": "123 Main St, Singapore",
        "phone": "+6591234567",
        "leave_balances": {
            "vacation": {"accrued": 20, "used": 5, "remaining": 15},
            "sick": {"accrued": 14, "used": 2, "remaining": 12}
        }
    },
    "EMP002": {
        "employee_id": "EMP002",
        "name": "John Smith",
        "email": "john.smith@altostrat.com",
        "department": "Sales",
        "role": "Sales Associate",
        "manager": "EMP003",
        "hire_date": "2024-01-10",
        "address": "456 Orchard Rd, Singapore",
        "phone": "+6587654321",
        "leave_balances": {
            "vacation": {"accrued": 10, "used": 9, "remaining": 1},
            "sick": {"accrued": 14, "used": 13, "remaining": 1}
        }
    },
    "EMP003": {
        "employee_id": "EMP003",
        "name": "Bob Vance",
        "email": "bob.vance@altostrat.com",
        "department": "Engineering",
        "role": "Engineering Manager",
        "manager": None,
        "hire_date": "2018-06-01",
        "address": "789 Serangoon Lane, Singapore",
        "phone": "+6598765432",
        "leave_balances": {
            "vacation": {"accrued": 25, "used": 10, "remaining": 15},
            "sick": {"accrued": 14, "used": 0, "remaining": 14}
        }
    },
    "EMP004": {
        "employee_id": "EMP004",
        "name": "Vidya M H",
        "email": "vidyamh@altostrat.com",
        "department": "Engineering",
        "role": "Lead Architect",
        "manager": None,
        "hire_date": "2021-08-01",
        "address": "12 Pasir Panjang Rd, Singapore",
        "phone": "+6591112222",
        "leave_balances": {
            "vacation": {"accrued": 22, "used": 4, "remaining": 18},
            "sick": {"accrued": 14, "used": 1, "remaining": 13}
        }
    }
}

MOCK_LEAVE_REQUESTS = []

# Email format check (RFC 5322)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
# Phone format check (E.164: + followed by 1 to 15 digits)
PHONE_REGEX = re.compile(r"^\+[1-9]\d{1,14}$")


def retrieve_employee_profile(employee_id: str) -> Optional[Dict[str, Any]]:
    """Fetch profile & contact information."""
    emp = MOCK_EMPLOYEE_DB.get(employee_id)
    if not emp:
        return None
    # Return profile info without internal leave balances
    profile = emp.copy()
    profile.pop("leave_balances", None)
    return profile


def update_contact_info(employee_id: str, new_address: Optional[str] = None, new_phone: Optional[str] = None) -> Dict[str, Any]:
    """Modify address and/or phone number with E.164 and structured checks."""
    emp = MOCK_EMPLOYEE_DB.get(employee_id)
    if not emp:
        return {"success": False, "error": f"Employee {employee_id} not found."}
    
    if new_phone:
        if not PHONE_REGEX.match(new_phone):
            return {"success": False, "error": f"Invalid phone format: '{new_phone}'. Must be in E.164 format (e.g. +6591234567)"}
        emp["phone"] = new_phone

    if new_address:
        if len(new_address.strip()) < 5:
            return {"success": False, "error": "Address is too short or invalid."}
        emp["address"] = new_address

    return {
        "success": True,
        "employee_id": employee_id,
        "updated_address": new_address,
        "updated_phone": new_phone
    }


def query_time_off_balances(employee_id: str) -> Optional[Dict[str, Any]]:
    """Fetch vacation & sick balances: accrued, used, remaining."""
    emp = MOCK_EMPLOYEE_DB.get(employee_id)
    if not emp:
        return None
    return emp.get("leave_balances")


def submit_leave_request(
    employee_id: str, start_date_str: str, end_date_str: str, leave_type: str, work_days: int
) -> Dict[str, Any]:
    """Submit a leave request check balances and dates."""
    emp = MOCK_EMPLOYEE_DB.get(employee_id)
    if not emp:
        return {"success": False, "error": f"Employee {employee_id} not found."}
    
    # Parse dates
    try:
        start_date = datetime.date.fromisoformat(start_date_str)
        end_date = datetime.date.fromisoformat(end_date_str)
    except ValueError:
        return {"success": False, "error": "Dates must be in ISO format (YYYY-MM-DD)"}
    
    # Temporal Validity check
    if start_date > end_date:
        return {"success": False, "error": "Start date must be before or equal to end date"}
    
    today = datetime.date.today()
    if start_date < today:
        return {"success": False, "error": "Past-dated requests are blocked."}
    
    # Type validity
    leave_type = leave_type.lower().strip()
    if leave_type not in ("vacation", "sick"):
        return {"success": False, "error": "Invalid leave type. Must be 'vacation' or 'sick'"}
    
    # Balance constraint check
    balances = emp.get("leave_balances", {})
    balance = balances.get(leave_type, {}).get("remaining", 0)
    
    if work_days > balance:
        return {
            "success": False, 
            "error": f"Insufficient {leave_type} balance. Requested {work_days} days, remaining {balance} days.",
            "requested_days": work_days,
            "remaining_days": balance
        }
    
    # Process leave request (decrement balance)
    balances[leave_type]["remaining"] -= work_days
    balances[leave_type]["used"] += work_days
    
    request_id = f"LR-{len(MOCK_LEAVE_REQUESTS) + 1001}"
    req = {
        "request_id": request_id,
        "employee_id": employee_id,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "leave_type": leave_type,
        "work_days": work_days,
        "status": "APPROVED"
    }
    MOCK_LEAVE_REQUESTS.append(req)
    return {
        "success": True, 
        "request_id": request_id, 
        "status": "APPROVED",
        "employee_id": employee_id,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "leave_type": leave_type,
        "work_days": work_days
    }
