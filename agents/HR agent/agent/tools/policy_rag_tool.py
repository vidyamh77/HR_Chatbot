"""Policy document retrieval tools."""
from typing import Dict, Any, List
from .. import config

# Mock Policy Documents Corpus
MOCK_POLICIES = [
    {
        "title": "Altostrat Singapore Paid Time Off and Leave Policy",
        "section": "Bereavement Leave",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#bereavement",
        "content": (
            "Altostrat Singapore provides paid bereavement leave for employees. "
            "Full-time employees are eligible for up to 5 consecutive working days of paid bereavement leave "
            "in the event of the death of an immediate family member (spouse, child, parent, sibling). "
            "For extended family members, employees are eligible for up to 2 working days. "
            "Documentation (e.g., death certificate) may be requested by HR."
        ),
        "keywords": ["bereavement", "funeral", "death", "mourning", "compassionate"]
    },
    {
        "title": "Altostrat Singapore Remote Work Policy",
        "section": "Remote Work Eligibility & Allowances",
        "link": "https://altostrat.sharepoint.com/hr/policies/remote-work#eligibility",
        "content": (
            "Employees classified as 'Remote' in their employment contract are eligible for hardware procurement. "
            "Eligible remote employees may request a standard home office setup, including one external monitor (up to 27 inches), "
            "a standard keyboard, and a mouse. Requests must be submitted via ServiceImmediately and approved by the department head. "
            "The employee profile in WorkWeek must reflect a 'Remote' status to qualify."
        ),
        "keywords": ["remote", "monitor", "home office", "procurement", "hardware", "keyboard", "mouse"]
    },
    {
        "title": "Altostrat Singapore Medical Leave Policy",
        "section": "Short-Term Medical Leave Procedures",
        "link": "https://altostrat.sharepoint.com/hr/policies/medical-leave#short-term",
        "content": (
            "Employees are eligible for up to 14 days of paid outpatient sick leave per calendar year. "
            "To request short-term medical leave, the employee must: "
            "1. Inform their manager before 9:00 AM on the first day of absence. "
            "2. Submit a Leave of Absence request in WorkWeek within 2 working days of return. "
            "3. Upload a valid Medical Certificate (MC) from a registered medical practitioner in WorkWeek. "
            "4. For leaves exceeding 3 consecutive days, open a ServiceImmediately ticket to trigger notification and routing for email/manager coverage."
        ),
        "keywords": ["medical", "sick", "doctor", "mc", "medical certificate", "hospitalisation", "short-term"]
    },
    {
        "title": "Altostrat Singapore Relocation Policy",
        "section": "Relocation Allowances & Procedures",
        "link": "https://altostrat.sharepoint.com/hr/policies/relocation#allowance",
        "content": (
            "Employees transferring permanently to another global office (e.g., London) are eligible for relocation benefits. "
            "The relocation allowance for permanent transfers to London is capped at SGD 10,000 to cover shipment and travel. "
            "To execute a transfer, the employee must: "
            "1. Complete and sign the Relocation Agreement. "
            "2. Update their primary residential address in WorkWeek to the target city within 5 days of arrival. "
            "3. Open a facilities badge ticket in ServiceImmediately to request office building access keys in the target location."
        ),
        "keywords": ["relocation", "transfer", "london", "allowance", "moving", "badge", "building access"]
    },
    {
        "title": "Altostrat Singapore Business Courtesies & Expenses Guideline",
        "section": "Host Gifts and Business Entertainment Spend Limits",
        "link": "https://altostrat.sharepoint.com/hr/policies/expenses#gifts",
        "content": (
            "Business courtesies, including host gifts, are reimbursable up to a maximum limit of SGD 50 per event. "
            "Reimbursement requests must be accompanied by itemized receipts. "
            "Any host gift exceeding SGD 50 requires pre-approval from the Compliance Department."
        ),
        "keywords": ["gift", "host", "business courtesy", "expense", "reimbursement", "spend limit", "$50"]
    },
    {
        "title": "Altostrat Singapore Business Courtesies & Expenses Guideline",
        "section": "Strictly Prohibited Spending Categories",
        "link": "https://altostrat.sharepoint.com/hr/policies/expenses#prohibited",
        "content": (
            "Certain spend categories are strictly prohibited from reimbursement, regardless of the transaction amount. "
            "Under no circumstances shall Altostrat reimburse expenses for: "
            "1. Gift cards, gift certificates, or pre-paid cash vouchers. "
            "2. Adult entertainment, including hostess bars, room salons, cabaret clubs, and adult clubs. "
            "3. Personal services or unauthorized recreational activities. "
            "Any submission containing prohibited items will be rejected and may result in disciplinary action."
        ),
        "keywords": ["gift card", "prohibited", "adult entertainment", "room salon", "hostess bar", "voucher", "cabaret", "prohibition"]
    },
    {
        "title": "Altostrat Singapore Childcare Leave Policy",
        "section": "Allowance Categories & Usage",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#childcare",
        "content": (
            "Paid childcare leave is available for eligible parents with children under the age of 12. "
            "Allowance categories: "
            "1. 6 days of paid leave per year if your children are under 7 years old. "
            "2. 2 days of paid leave per year if your youngest child is between 7 and 12 years old. "
            "3. 6 days of paid leave per year if you have children in both age groups. "
            "Usage: Leave is counted in full work days. Once agreed with your manager, you must record it in WorkWeek. "
            "Unused childcare leave does not carry over and is not paid out upon leaving the company."
        ),
        "keywords": ["childcare", "child", "parents", "under 12", "infant", "toddler", "kids", "youngest"]
    },
    {
        "title": "Altostrat Singapore Time Off in Lieu (TOIL) Policy",
        "section": "TOIL Accumulation and Usage Rules",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#toil",
        "content": (
            "If you are required by the business to work on a public holiday or during the weekend, "
            "you can claim time off in lieu to compensate for working outside your contractual hours. "
            "TOIL is granted and taken at your manager's discretion. "
            "There is no need to enter TOIL in WorkWeek; you must talk with your manager to agree on the time off "
            "and use your TOIL days before logging additional vacation days."
        ),
        "keywords": ["toil", "time off in lieu", "weekend work", "public holiday", "overtime", "weekend"]
    },
    {
        "title": "Altostrat Singapore Maternity Leave Policy",
        "section": "Maternity Leave Duration and Shared Parental Leave (SPL)",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#maternity",
        "content": (
            "Effective 1 April 2026, all eligible employees are entitled to 24 weeks of paid parental leave. "
            "Under Phase 2 of Singapore’s MSF scheme, parents of Singaporean children born on or after 1 April 2026 "
            "are entitled to 10 weeks of shared parental leave (SPL) (default split is 5 weeks for each parent). "
            "SPL Donation: If your spouse donates their portion (up to 10 weeks) of SPL to you, your total paid maternity "
            "leave can be extended to 25 or 26 weeks. SPL Allocation Audit: Regardless of the split, you must submit "
            "proof of the official SPL allocation from LifeSG within 4 weeks of birth/adoption. "
            "Interns who have served for a continuous period of at least 3 months are entitled to 16 weeks of statutory maternity leave. "
            "Administrative Procedures: Maternity leave can begin up to 28 days before your expected due date. "
            "The first 8 weeks (56 days) must be taken consecutively. The remaining 16 weeks (80 working days) can be "
            "taken flexibly in daily increments over a 12-month period following the child's birth. "
            "Maternity leave must be logged in WorkWeek using two separate codes: 'Singapore Leaves > SG - Maternity Leave (First 8 weeks)' "
            "and 'Singapore Leaves > SG - Maternity Leave (80 working days)'."
        ),
        "keywords": ["maternity", "parental leave", "pregnancy", "childbirth", "birth", "mother", "moms", "spl", "shared parental leave", "lifesg", "24 weeks", "baby"]
    },
    {
        "title": "Altostrat Singapore Baby Bonding Leave Policy",
        "section": "Baby Bonding Leave Allowances and Timelines",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#baby-bonding",
        "content": (
            "Baby Bonding Leave (BBL) is available to spent time with a new child welcomed through childbirth, "
            "adoption, surrogacy, or fostering (for parents who do not take maternity leave). "
            "Allowance: Eligible employees can take up to 18 weeks (90 work days) of paid leave per year. "
            "Even if multiple children are welcomed at once, only one 18-week period can be claimed. "
            "Timelines: BBL must begin on or after the child's birth/placement date and be fully utilized within "
            "12 months of that date, or any remaining balance is forfeited. It can be taken all at once or in weekly blocks. "
            "Shared Parental Leave Impact (Singapore): Your baby bonding leave remains at 18 weeks regardless of the SPL "
            "sharing arrangement with your spouse. However, if both parents are Altostrat employees and the father "
            "allocates SPL to his partner, his BBL must be reduced to 16 or 17 weeks. "
            "Benefit: Employees taking BBL are eligible for a monetary baby bonding benefit. "
            "Administrative Coverage: For planned medical leaves extending beyond a standard work week, employees are "
            "required to ensure business continuity by opening an administrative ticket (Category: 'HRSD', Priority: '3 - Moderate') "
            "to request a temporary email delegation to their direct manager."
        ),
        "keywords": ["baby bonding", "bonding leave", "bbl", "father", "dad", "adoption", "surrogacy", "fostering", "18 weeks", "90 work days", "hrsd", "parental"]
    },
    {
        "title": "Altostrat Singapore Ramp-Back Time Policy",
        "section": "Ramp-Back Eligibility and Duration",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#ramp-back",
        "content": (
            "To ease the transition back to work following a long leave, Altostrat offers ramp-back time. "
            "Eligibility: Employees must have taken at least 10 consecutive weeks of maternity, adoption, parental, "
            "or baby bonding leave. Duration and Schedule: You can take up to 2 weeks of paid ramp-back time "
            "immediately upon your return. During these 2 weeks, you must work a minimum of 50% of your normal weekly hours "
            "but will receive 100% of your normal salary. WorkWeek Entry: Salaried employees must enter the hours "
            "not worked in WorkWeek under the type 'Ramp Back Time' with the reason 'Baby Bonding Leave'. "
            "Hourly employees log this on their timecard in gTime."
        ),
        "keywords": ["ramp-back", "ramp back", "transition", "return to work", "reduced hours", "50%"]
    },
    {
        "title": "Altostrat Singapore Carer's Leave Policy",
        "section": "Carer's Leave Allowances and Attestation",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#carer",
        "content": (
            "Eligible employees can take up to 8 weeks of paid leave per loved one (family member, partner, dependent) "
            "per lifetime to care for seriously or terminally ill individuals. Leave is counted in work days and can be "
            "requested in weekly blocks or daily schedules. The minimum duration is half a work day. "
            "You may be asked to provide written attestation or medical documentation verifying the serious health condition. "
            "Do not share sensitive medical details when contacting support."
        ),
        "keywords": ["carer", "care", "seriously ill", "terminally ill", "loved one", "family care", "8 weeks", "illness"]
    },
    {
        "title": "Altostrat Singapore Unpaid Time Off and Personal Leave Policy",
        "section": "Short-Term Unpaid Time Off & Long-Term Personal Leave Limits",
        "link": "https://altostrat.sharepoint.com/hr/policies/leave-policy#unpaid",
        "content": (
            "When accrued vacation is exhausted or low, employees may request unpaid leaves of absence. "
            "Unpaid Time Off (Short-Term): With manager approval, you can take up to 30 calendar days of unpaid time off. "
            "This can be taken continuously or in daily increments. Personal Leave (Long-Term): Requests to extend "
            "unpaid time off past 30 days reclassify the entire leave as a personal leave. Limits: With manager and director "
            "approval, employees can request up to 92 calendar days of continuous unpaid personal leave (inclusive of "
            "any unpaid time off already taken). Personal leave must be taken in one continuous block of time. "
            "Prerequisites: You typically need at least 2 years of tenure and to have received a 'Significant Impact' "
            "or higher rating in your last GRAD performance cycle to qualify. It is highly recommended that you have "
            "fewer than 10 vacation days remaining in your balance before unpaid leaves are approved."
        ),
        "keywords": ["unpaid leave", "personal leave", "unpaid time off", "92 days", "30 days", "tenure", "exhausted vacation", "unpaid"]
    },
    {
        "title": "Altostrat Singapore Anti-Bribery and Government Ethics Policy",
        "section": "Written Pre-Approval Requirements for Government Officials",
        "link": "https://altostrat.sharepoint.com/hr/policies/ethics#anti-bribery",
        "content": (
            "Altostrat has a strict zero-tolerance policy for bribery and corruption. The Golden Rule: Never offer, "
            "promise, give, or receive anything of value to/from a government official to obtain or retain an "
            "improper advantage. Facilitation payments are strictly prohibited. Written Pre-Approval Requirements: "
            "1. U.S. Government Officials: Written pre-approval is required before offering anything of value of any "
            "amount (except non-alcoholic drinks at an Altostrat office meeting). 2. Non-U.S. Government Officials: "
            "Pre-approval is required if the value exceeds US $100, or if cumulative courtesies to that official exceed "
            "US $200 within a rolling 6-month period."
        ),
        "keywords": ["bribery", "corruption", "government official", "facilitation payments", "pre-approval", "ethics", "u.s."]
    },
    {
        "title": "Altostrat Singapore Travel and Expense Policy",
        "section": "Meal Allowances, Group Meals, and Aged Claims Approvals",
        "link": "https://altostrat.sharepoint.com/hr/policies/expenses#limits",
        "content": (
            "Daily Meal Limit: Reimbursement for individual meals on global business trips is capped at US $120 "
            "per employee per day. All meal expenses must be individually detailed with receipts. Group Meals with "
            "Altostrat Colleagues: Group meals are capped at US $120 per employee per day. The most senior colleague "
            "present must pay and submit the expense. VP Pre-Approval for High-Value Events: Any group meal or "
            "customer entertainment event costing US $500 or greater per head requires written, pre-event approval from your VP. "
            "Aged Expense Approvals: Out-of-pocket claims older than 60 days require Director approval. "
            "Claims older than 90 days require VP approval. Claims older than one year are non-reimbursable."
        ),
        "keywords": ["travel expense", "meal allowance", "group meals", "aged claims", "vp approval", "director approval", "$120", "$500", "concur"]
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
