"""Policy document retrieval tools."""
from typing import Dict, Any, List
from .. import config

# Mock Policy Documents Corpus
MOCK_POLICIES = [
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 1.1: Outpatient Sick Time & Hospitalization Leave (Singapore)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#sick-leave",
        "content": (
            "Altostrat Singapore provides paid sick leave to support your health and recovery when you are medically certified as unfit for work. "
            "Outpatient Sick Leave Allowance: Eligible employees and interns receive up to 14 days of paid outpatient sick leave per calendar year, compensated at 100% of their base salary. Part-time and fixed-term employees' leave is prorated based on their contracted working hours. "
            "Hospitalization Leave Allowance: Employees can utilize an additional 46 work days of paid hospitalization leave per year. This is not an extension of outpatient sick leave but is granted for inpatient stays, day surgeries, quarantine orders, or serious medical conditions certified by a medical practitioner employed by an approved hospital. "
            "Notification Requirements: You must notify your manager that you need to take sick or hospitalization leave at least one hour before your normal start time. If your manager is unavailable, you must contact support. "
            "Medical Certificate (MC) Submission: "
            "If you are sick for more than two work days, you must submit your sick certificate from a registered medical practitioner via WorkWeek. "
            "This certificate must be submitted within 48 hours of taking the leave. "
            "Altostrat reserves the right to decline paid sick leave or classify the absence as unpaid if the MC is not submitted. Unapproved absences can result in disciplinary action."
        ),
        "keywords": ["sick leave", "hospitalization", "outpatient", "medical certificate", "mc", "illness", "unfit for work"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 1.2: Paid Vacation Leave (Singapore)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#vacation",
        "content": (
            "Vacation time is provided to help employees detach from work and recharge. Employees earned their full vacation entitlement for the year on January 1. "
            "Accrual Tier Matrix: The number of days accrued is based on years of continuous service: "
            "1 to 6 years of service: 20 days per year. "
            "7 to 10 years of service: 21 days per year. "
            "11+ years of service: 22 days per year. "
            "Proration: Employees in their first year of service receive a prorated number of vacation days based on their start date. Part-time employees accrue prorated hours based on their individual FTE percentage (e.g., 50% FTE accrues 50% of the vacation rate). "
            "Booking and Scheduling Rules: "
            "Vacation can be taken in half-day or full-day increments. "
            "Shift workers must book vacation based on actual shift hours. For instance, a 12-hour shift requires 1.5 vacation days (defined as 8-hour blocks). "
            "You must discuss and obtain approval from your manager for your planned dates at least 15 days in advance. "
            "Any changes or cancellations to booked vacation must be processed at least 15 days before the leave starts. "
            "Carryover & Pay-out Limitations: All unused vacation days from the current year carry over for exactly one additional year. Carried-over days must be used by December 31 of the following year or they are forfeited. Altostrat does not pay out unused vacation, except upon country-to-country transfer or termination of employment. "
            "Floating Holidays: If a recognized public holiday falls on a Saturday or Sunday, employees are granted a floating holiday, which must be utilized like vacation before the calendar year ends. Floating holidays do not carry forward and are not cashed out upon termination. "
            "System Constraints & Validity: All leave requests must be chronologically valid (the start date cannot occur after the end date). Furthermore, the system will automatically reject any leave request that exceeds the employee's current accrued balance."
        ),
        "keywords": ["vacation leave", "accrual tier", "proration", "floating holiday", "carryover", "payout", "schedule vacation"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 1.3: Childcare Leave (Singapore)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#childcare",
        "content": (
            "Paid childcare leave is available for eligible parents with children under the age of 12. "
            "Allowance Categories: "
            "6 days of paid leave per year if your children are under 7 years old. "
            "2 days of paid leave per year if your youngest child is between 7 and 12 years old. "
            "6 days of paid leave per year if you have children in both age groups. "
            "Usage: Leave is counted in full work days. Once agreed with your manager, you must record it in WorkWeek. Unused childcare leave does not carry over and is not paid out upon leaving the company."
        ),
        "keywords": ["childcare leave", "parents", "under 12", "allowance", "WorkWeek"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 1.4: Time Off in Lieu (TOIL) (Singapore)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#toil",
        "content": (
            "If you are required by the business to work on a public holiday or during the weekend, you can claim time off in lieu to compensate for working outside your contractual hours. "
            "TOIL is granted and taken at your manager's discretion. "
            "There is no need to enter TOIL in WorkWeek; you must talk with your manager to agree on the time off and use your TOIL days before logging additional vacation days."
        ),
        "keywords": ["toil", "time off in lieu", "weekend work", "public holiday", "overtime"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 2.1: Maternity Leave (Singapore)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#maternity",
        "content": (
            "Paid maternity leave is offered to support pregnancy, recovery from childbirth, and infant bonding. "
            "Duration: Effective 1 April 2026, all eligible employees are entitled to 24 weeks of paid parental leave. "
            "Shared Parental Leave (SPL) Extension: Under Phase 2 of Singapore’s MSF scheme, parents of Singaporean children born on or after 1 April 2026 are entitled to 10 weeks of shared parental leave (default split is 5 weeks for each parent). "
            "SPL Donation: If your spouse donates their portion (up to 10 weeks) of SPL to you, your total paid maternity leave can be extended to 25 or 26 weeks. "
            "SPL Allocation Audit: Regardless of the split, you must submit proof of the official SPL allocation from LifeSG within 4 weeks of birth/adoption for record-keeping and statutory audits. "
            "Moms Donating SPL: If you donate your portion of SPL to your spouse, your Altostrat maternity leave is not reduced below the 24-week baseline, as company benefits are already inclusive of and exceed statutory limits. "
            "Interns: Eligible interns who have served for a continuous period of at least 3 months are entitled to 16 weeks of statutory maternity leave, which must be taken consecutively. Interns whose spouses donate SPL can extend their leave up to 26 weeks. "
            "Administrative Procedures: "
            "Maternity leave can begin up to 28 days before your expected due date. "
            "The first 8 weeks (56 days) must be taken consecutively. The remaining 16 weeks (80 working days) can be taken flexibly in daily increments over a 12-month period following the child's birth. "
            "Maternity leave must be logged in WorkWeek using two separate codes: 'Singapore Leaves > SG - Maternity Leave (First 8 weeks)' and 'Singapore Leaves > SG - Maternity Leave (80 working days)'."
        ),
        "keywords": ["maternity leave", "parental leave", "pregnancy", "spl", "shared parental leave", "lifesg", "24 weeks", "16 weeks", "interns"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 2.2: Baby Bonding Leave (Global)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#baby-bonding",
        "content": (
            "Baby Bonding Leave (BBL) is available to spent time with a new child welcomed through childbirth, adoption, surrogacy, or fostering (for parents who do not take maternity leave). "
            "Allowance: Eligible employees can take up to 18 weeks (90 work days) of paid leave per year. Even if multiple children are welcomed at once, only one 18-week period can be claimed. "
            "Timelines: BBL must begin on or after the child's birth/placement date and be fully utilized within 12 months of that date, or any remaining balance is forfeited. It can be taken all at once or in weekly blocks. "
            "Shared Parental Leave Impact (Singapore): Your baby bonding leave remains at 18 weeks regardless of the SPL sharing arrangement with your spouse. However, if both parents are Altostrat employees and the father allocates SPL to his partner, his BBL must be reduced to 16 or 17 weeks depending on the allocation, subject to periodic audits. "
            "Monetary Benefit: Employees taking BBL are eligible for a monetary baby bonding benefit to spend on meals, cleaning, laundry, or gardening. "
            "Administrative Coverage: For planned medical leaves extending beyond a standard work week, employees are required to ensure business continuity. To do this, employees must open an administrative ticket (Category: 'HRSD', Priority: '3 - Moderate') to request a temporary email delegation to their direct manager."
        ),
        "keywords": ["baby bonding leave", "bbl", "fostering", "adoption", "18 weeks", "monetary benefit", "email delegation"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 2.3: Ramp-Back Time (Global)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#ramp-back",
        "content": (
            "To ease the transition back to work following a long leave, Altostrat offers ramp-back time. "
            "Eligibility: Employees must have taken at least 10 consecutive weeks of maternity, adoption, parental, or baby bonding leave. "
            "Duration and Schedule: You can take up to 2 weeks of paid ramp-back time immediately upon your return. During these 2 weeks, you must work a minimum of 50% of your normal weekly hours but will receive 100% of your normal salary. "
            "WorkWeek Entry: Salaried employees must enter the hours not worked in WorkWeek under the type 'Ramp Back Time' with the reason 'Baby Bonding Leave'. Hourly employees log this on their timecard in gTime."
        ),
        "keywords": ["ramp-back time", "transition", "reduced schedule", "50% hours", "maternity", "baby bonding"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 3.1: Bereavement Leave (Global)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#bereavement",
        "content": (
            "Paid bereavement leave is provided to support employees during times of grief. "
            "Allowance: Employees can take up to 4 weeks (20 work days for a standard 5-day schedule) of paid leave per event. This applies to the loss of a close loved one, including pregnancy loss (miscarriage or stillbirth). "
            "Timeline: Bereavement leave must be taken within 12 months of the death. "
            "Pet Loss: Paid bereavement leave does not apply to pet loss. Vacation, unpaid time off, or flexible schedules should be arranged with managers in those instances."
        ),
        "keywords": ["bereavement leave", "grief", "pet loss", "miscarriage", "4 weeks", "20 work days"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 3.2: Carer's Leave (Global)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#carer",
        "content": (
            "Eligible employees can take up to 8 weeks of paid leave per loved one (family member, partner, dependent) per lifetime to care for seriously or terminally ill individuals. "
            "Leave is counted in work days and can be requested in weekly blocks or daily schedules. The minimum duration is half a work day. "
            "You may be asked to provide written attestation or medical documentation verifying the serious health condition. Do not share sensitive medical details when contacting support."
        ),
        "keywords": ["carer's leave", "seriously ill", "dependency", "8 weeks", "attestation"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 3.3: Unpaid Time Off & Personal Leave (Global)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#unpaid",
        "content": (
            "When accrued vacation is exhausted or low, employees may request unpaid leaves of absence. "
            "Unpaid Time Off (Short-Term): With manager approval, you can take up to 30 calendar days of unpaid time off. This can be taken continuously or in daily increments. "
            "Personal Leave (Long-Term): Requests to extend unpaid time off past 30 days reclassify the entire leave as a personal leave. "
            "Limits: With manager and director approval, employees can request up to 92 calendar days of continuous unpaid personal leave (inclusive of any unpaid time off already taken). Personal leave must be taken in one continuous block. "
            "Prerequisites: You typically need at least 2 years of tenure and to have received a 'Significant Impact' or higher rating in your last GRAD performance cycle to qualify. "
            "It is highly recommended that you have fewer than 10 vacation days remaining in your balance before unpaid leaves are approved. Personal leave cannot be used as a substitute for flexible work schedules or medical accommodations."
        ),
        "keywords": ["unpaid time off", "personal leave", "92 days", "30 days", "tenure", "GRAD rating"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 4.1 & 4.3: Travel Booking & Lodging Caps",
        "link": "https://altostrat.sharepoint.com/hr/policies/expenses#lodging",
        "content": (
            "Booking Timelines: Air and hotel bookings must be completed at least 3 weeks in advance to secure reasonable rates. Discuss the trip with your manager, travel cap is 120USD per day for meals, create a ticket request as Travel from ITSM, and review the global risk map before departing. "
            "Company Card Mandate: Employees who incur significant business expenses (>$10,000 per quarter) or single transactions over $5,000 must use their Company Card for their travel spend. "
            "Staying with Friends/Family: Staying with a friend or relative in lieu of a hotel allows you to buy a host gift of up to US $50 per day, backed by valid receipts. Cash or gift card host gifts are strictly prohibited."
        ),
        "keywords": ["travel booking", "advance booking", "company card", "host gift", "lodging", "$50"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 4.4: Meal Allowances & Entertainment",
        "link": "https://altostrat.sharepoint.com/hr/policies/expenses#limits",
        "content": (
            "Daily Meal Limit: Reimbursement for individual meals on global business trips is capped at US $120 (or equivalent) per employee per day. This is not a per diem; all meal expenses must be individually detailed with receipts. "
            "Group Meals with Altostrat Colleagues: Group meals are capped at US $120 per employee per day. You must list all attending colleagues in Concur for tax compliance. The most senior colleague present (highest level) must pay and submit the expense to ensure independent manager approval. "
            "VP Pre-Approval for High-Value Events: Any group meal or customer entertainment event costing US $500 or greater per head requires written, pre-event approval from your VP, which must be attached to the Concur expense report."
        ),
        "keywords": ["meal allowance", "daily meal limit", "group meal", "VP pre-approval", "concur", "US $120", "entertainment"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 5.1: Anti-Bribery & Government Ethics",
        "link": "https://altostrat.sharepoint.com/hr/policies/ethics#anti-bribery",
        "content": (
            "Altostrat has a strict zero-tolerance policy for bribery and corruption. Never offer, promise, give, or receive anything of value to/from a government official to obtain or retain an improper advantage. 'Facilitation' or 'grease' payments to expedite routine actions are strictly prohibited. "
            "Written Pre-Approval Requirements: "
            "1. U.S. Government Officials: Written pre-approval is required before offering anything of value of any amount (except non-alcoholic drinks at an Altostrat office meeting). "
            "2. Non-U.S. Government Officials: Pre-approval is required if the value exceeds US $100, or if cumulative courtesies to that official exceed US $200 within a rolling 6-month period."
        ),
        "keywords": ["bribery", "corruption", "government official", "grease payments", "pre-approval", "compliance", "US $100"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 5.2: Commercial Gifts & Entertainment (Non-Government Recipients)",
        "link": "https://altostrat.sharepoint.com/hr/policies/expenses#commercial-gifts",
        "content": (
            "Adult Entertainment & Gambling Prohibitions: Business courtesies must never involve gambling, adult entertainment (strip clubs, hostess bars, room salons), cash, or cash equivalents (gift cards or certificates). "
            "Frequency Limit: You may not exchange business courtesies with the same customer or business partner more than twice in any 3-month period. "
            "Written Pre-Approval Thresholds (Non-Government): "
            "Under US $100 per person: No pre-approval required. "
            "US $100 to US $250 per person: Written pre-approval from the employee's Manager. "
            "US $250 to US $500 per person: Written pre-approval from the employee's Director. "
            "Over US $500 per person: Written pre-approval from the employee's VP."
        ),
        "keywords": ["commercial gifts", "gambling", "adult entertainment", "pre-approval thresholds", "non-government"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 5.4: Remote Work, Telework, & Data Security",
        "link": "https://altostrat.sharepoint.com/hr/policies/remote-work#security",
        "content": (
            "Public Settings Restriction: Do not work on Altostrat confidential or proprietary projects in public settings (such as coffee shops or public libraries). "
            "Privacy Guardrails: When working away from the office, you must use a privacy screen, wear headphones during virtual meetings, and keep sensitive documents physically secured. "
            "Home Office Equipment Allowance: Employees with an approved 'Remote' or 'Hybrid' location status are eligible for a $500 USD allowance for home office equipment, including monitors. All remote equipment orders must be submitted via a 'Facilities' category ticket and shipped directly to the employee's verified remote shipping address."
        ),
        "keywords": ["remote work", "telework", "public settings", "privacy screen", "home office allowance", "$500 USD", "monitors"]
    },
    {
        "title": "Altostrat Singapore Employee Policy Handbook & Conduct Guidelines",
        "section": "SECTION 5.5: Community Guidelines (Conversational Boundaries)",
        "link": "https://altostrat.sharepoint.com/hr/policies/ethics#community",
        "content": (
            "WorkWeek Productivity: Disrupting the WorkWeek to engage in raging debates over politics or non-work topics is prohibited. Our primary responsibility is to do the work we were hired to do. "
            "No Trolling: Employees must not troll, name-call, or engage in ad hominem attacks against any coworker, business partner, or public figure. This includes any demeaning or humiliating remarks."
        ),
        "keywords": ["community guidelines", "conversational boundaries", "trolling", "political debates", "ad hominem"]
    }
]

def search_policy_docs(query: str) -> Dict[str, Any]:
    """Search the HR policy corpus. Supports local mock matching or Vertex AI Search.

    Args:
        query: A natural-language policy question or search phrase.

    Returns:
        A dictionary containing 'grounded_context' and 'citations'.
    """
    if config.RETRIEVAL_MODE == "mock":
        return _mock_search_policy_docs(query)
    else:
        return _vertex_search_policy_docs(query)


def _mock_search_policy_docs(query: str) -> Dict[str, Any]:
    """A keyword-based mock search engine over in-memory policies."""
    query_lower = query.lower()
    matched_chunks = []
    citations = []

    for doc in MOCK_POLICIES:
        # Check if query contains any of the keywords or parts of title/section
        score = 0
        for kw in doc["keywords"]:
            if kw in query_lower:
                score += 2
        if doc["section"].lower() in query_lower:
            score += 3
        
        if score > 0:
            matched_chunks.append((score, doc))

    # Sort matched chunks by score descending
    matched_chunks.sort(key=lambda x: x[0], reverse=True)
    
    context_parts = []
    for score, doc in matched_chunks[:3]:  # Top 3 matches
        citations.append(doc["link"])
        context_parts.append(
            f"Source: {doc['title']} - Section: {doc['section']}\n"
            f"Link: {doc['link']}\n"
            f"Content: {doc['content']}"
        )

    grounded_context = "\n\n".join(context_parts)
    return {
        "grounded_context": grounded_context,
        "citations": list(set(citations))
    }


def _vertex_search_policy_docs(query: str) -> Dict[str, Any]:
    """Vertex AI Search discovery engine client."""
    from google.api_core.client_options import ClientOptions
    from google.cloud import discoveryengine_v1 as discoveryengine

    project_id = config.GOOGLE_CLOUD_PROJECT
    location = config.VERTEX_AI_SEARCH_LOCATION
    engine_id = config.VERTEX_AI_SEARCH_ENGINE_ID

    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    serving_config = (
        f"projects/{project_id}/locations/{location}/collections/default_collection"
        f"/engines/{engine_id}/servingConfigs/default_search"
    )
    content_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_answer_count=3, max_extractive_segment_count=3
        )
    )
    request = discoveryengine.SearchRequest(
        serving_config=serving_config, query=query, page_size=3, content_search_spec=content_spec
    )
    
    response = client.search(request)

    context_parts = []
    citations = []

    for result in response.results:
        d = result.document.derived_struct_data
        link = d.get('link')
        if link:
            citations.append(link)
        
        segments = d.get('extractive_segments', [])
        for segment in segments:
            content = segment.get('content')
            if content:
                context_parts.append(f"Source: {link}\nContent: {content}")
                
    grounded_context = "\n\n".join(context_parts)
    return {
        "grounded_context": grounded_context,
        "citations": list(set(citations))
    }
