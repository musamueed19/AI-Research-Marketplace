# Company Search – Full Flow (HTML → View → Apollo API)

Yeh doc detail mein batata hai: HTML form se data kaise aata hai, view usse kya karta hai, aur har filter Apollo API tak kaise map hota hai.

---

## 1. HTML Form (company_search.html)

### Form tag
```html
<form method="POST" id="searchForm">
    {% csrf_token %}
    ...
</form>
```
- **Method**: POST  
- **Action**: nahi diya → same URL pe submit (root `/`, jo `company_search_view` pe map hai)  
- **CSRF**: Django CSRF token required hota hai POST ke liye  

### Form fields (company search ke liye)

| HTML / Form field | Form name (request.POST key) | Type | Example |
|-------------------|------------------------------|------|---------|
| Company Name | `company_name` | text | "Google" |
| Domains | `domains` | text (comma-separated) | "google.com, microsoft.com" |
| Locations (Include) | `locations_included` | text (comma-separated) | "Berlin, Germany" |
| Locations (Exclude) | `locations_excluded` | text (comma-separated) | "China, Russia" |
| Employees Min | `employees_min` | number | 10 |
| Employees Max | `employees_max` | number | 500 |
| Revenue Min ($M) | `revenue_min` | number | 1 |
| Revenue Max ($M) | `revenue_max` | number | 100 |
| Organization Keyword | `organization_keyword` | text (comma-separated) | "caster, software" |
| Industries (include) | `industries` | multi-select (list) | ["computer software", "financial services"] |
| Industries (exclude) | `industries_exclude` | multi-select (list) | ["retail"] |
| Page | `page` | number | 1 |
| Per page | `per_page` | choice (10/25/50/100) | 25 |

**Note:** Job Titles aur Seniorities form pe hain lekin **company search payload mein nahi jate** – yeh sirf baad mein contacts/people search ke liye use hote hain.

---

## 2. Django View (company_search_view)

### Request flow
1. User "Search Companies" dabata hai → browser same URL pe **POST** karta hai.
2. `company_search_view(request)` call hota hai.
3. `request.method == "POST"` → form validate hota hai.

### Form validation
```python
form = CompanySearchForm(request.POST)
if form.is_valid():
    data = form.cleaned_data   # cleaned types: int, list, etc.
```
- `request.POST` se raw string values aati hain.
- `CompanySearchForm` unhe validate karta hai (required, type, etc.).
- `cleaned_data` mein:
  - numbers → int
  - multi-select → list of values
  - text → trimmed string

### Location filter hone par extra settings
```python
loc_included = data.get("locations_included")
if loc_included:
    data = dict(data)
    data["per_page"] = 100   # Apollo se 100 per page maangte hain
    data["page"] = 1
```
- Jab user "Locations (Include)" mein kuch daalta hai:
  - **per_page** force **100** kar diya jata hai taaki ek request mein zyada results aayein.
  - **page** 1 set rehta hai (multi-page fetch view khud pages 2, 3 karega).

### Payload build
```python
payload = build_apollo_payload(data)
```
- `data` = form ka `cleaned_data` ( + location ke time per_page=100, page=1).
- `build_apollo_payload(data)` isi `data` se Apollo ke format mein ek single `payload` dict banata hai (detail niche).

### Apollo API call
```python
response = search_companies(payload)
```
- `apollo_service.search_companies(payload)` call hota hai.
- Apollo ka endpoint: `POST https://api.apollo.io/api/v1/mixed_companies/search`
- Body: `payload` (JSON).
- Response: `accounts`, `organizations`, `pagination`, etc.

### Merge + multi-page (location filter)
```python
accounts = list(response.get("accounts", []))
organizations = list(response.get("organizations", []))
_merge_page_items(accounts, organizations)

if loc_included and total_pages > 1:
    for page in range(2, min(4, total_pages + 1)):
        data["page"] = page
        next_response = search_companies(build_apollo_payload(data))
        next_accounts = next_response.get("accounts", [])
        next_organizations = next_response.get("organizations", [])
        _merge_page_items(accounts, next_accounts, next_organizations)
```
- Pehle response ki **accounts** + **organizations** ek hi list `accounts` mein merge (id se dedupe).
- Agar location filter hai aur Apollo ne 1 se zyada pages diye, to **page 2 aur 3** bhi same payload (sirf `page` change) se fetch karke `accounts` mein merge.

### Normalize + filter + count
```python
companies = normalize_companies(accounts)

if loc_included and len(accounts) > (pagination.get("per_page") or 100):
    total_count = len(companies)   # multi-page: sab dikhao, filter mat lagao
elif loc_included:
    terms = [x.strip() for x in loc_included.split(",") if x.strip()]
    companies = filter_companies_by_location(companies, terms)
    total_count = len(companies)
else:
    total_count = total_entries
```
- **normalize_companies**: Apollo ke account/org objects ko ek common shape mein (id, name, domain, city, state, country, searchable_location_string, revenue, etc.).
- **Location filter**:
  - Agar merged list size > per_page (e.g. 300 > 100) → koi extra location filter nahi, sab companies dikhao, `total_count = len(companies)`.
  - Agar sirf ek page jitna data → `filter_companies_by_location(companies, terms)` chalaya, `total_count = len(companies)`.
- Bina location filter → `total_count = total_entries` (Apollo wala total).

### Response
```python
return render(request, "apollo_ingest/company_search.html", {
    "form": form,
    "companies": companies,
    "total_count": total_count,
    "error": error,
})
```
- Template ko `companies` list aur `total_count` milte hain; table mein `{% for company in companies %}` se render hota hai.

---

## 3. Har filter ka detail: Form → build_apollo_payload → Apollo

### 3.1 Company Name
- **Form**: `company_name` (CharField, optional).
- **Payload**:  
  - Agar value hai: `payload["q_organization_name"] = company_name.strip()`  
  - Apollo: organization name par text search (e.g. "Google", "Microsoft").

### 3.2 Domains
- **Form**: `domains` (CharField, comma-separated, e.g. "google.com, microsoft.com").
- **Payload**:  
  - Split by comma, strip: `domain_list = [d.strip() for d in domains.split(",") if d.strip()]`  
  - Agar list non-empty: `payload["q_organization_domains_list"] = domain_list`  
  - Apollo: sirf in domains wale organizations.

### 3.3 Locations (Include)
- **Form**: `locations_included` (CharField, comma-separated, e.g. "Berlin, Germany").
- **Payload**:  
  - Split by comma, strip, **lowercase**: `loc_list = [x.strip().lower() for x in locations_included.split(",") if x.strip()]`  
  - Agar non-empty: `payload["organization_locations"] = loc_list`  
  - Apollo: companies jinka HQ/office in locations mein ho (e.g. `["berlin", "germany"]`).

### 3.4 Locations (Exclude)
- **Form**: `locations_excluded` (CharField, comma-separated).
- **Payload**:  
  - Same tarah list, lowercase: `payload["organization_not_locations"] = loc_list`  
  - Apollo: in locations wale exclude (e.g. India, China).

### 3.5 Employee Range
- **Form**: `employees_min`, `employees_max` (IntegerField, optional).
- **Payload**:  
  - Agar dono empty nahi:  
    - `min_val = employees_min if employees_min is not None else 1`  
    - `max_val = employees_max if employees_max is not None else 1000000`  
    - `payload["organization_num_employees_ranges"] = [f"{min_val},{max_val}"]`  
  - Apollo: employee count is range ke andar (format "min,max").

### 3.6 Revenue Range
- **Form**: `revenue_min`, `revenue_max` (IntegerField, **in millions $**).
- **Payload**:  
  - Agar dono empty nahi:  
    - `min_val = revenue_min if revenue_min is not None else 0`  
    - `max_val = revenue_max if revenue_max is not None else 999999`  
    - `payload["revenue_range"] = {"min": min_val, "max": max_val}`  
  - Apollo: revenue (Apollo typically millions mein interpret karta hai) is range ke andar.

### 3.7 Organization Keyword
- **Form**: `organization_keyword` (CharField, comma-separated, e.g. "caster, software").
- **Payload**:  
  - Split, strip: `tag_list = [t.strip() for t in organization_keyword.split(",") if t.strip()]`  
  - Agar non-empty: `payload["q_organization_keyword_tags"] = tag_list`  
  - Apollo: organization keyword/tags par filter (e.g. "software", "fintech").

### 3.8 Industries (Include)
- **Form**: `industries` (MultipleChoiceField – multi-select).
- **Payload**:  
  - List of selected values (e.g. `["computer software", "financial services"]`).  
  - Agar non-empty:  
    - `payload["filters"]` mein append:  
      - `id`: `"filter.account.industry_tags-is_any_of"`  
      - `field_id`: `"filter.account.industry_tags"`  
      - `operand_data_type`: `"multiselectlist"`  
      - `operator`: `"is_any_of"`  
      - `options`: industries list  
  - Apollo: industry_tags in mein se koi bhi ho to match.

### 3.9 Industries (Exclude)
- **Form**: `industries_exclude` (MultipleChoiceField).
- **Payload**:  
  - Same structure, lekin:  
    - `id`: `"filter.account.industry_tags-is_none_of"`  
    - `operator`: `"is_none_of"`  
    - `options`: industries_exclude list  
  - Apollo: in industries wale exclude.

### 3.10 Organization Job Titles (company search)
- **Form**: `organization_job_titles` (CharField, comma-separated).  
  - (HTML mein yeh row comment out hai, lekin form + payload dono support karte hain.)
- **Payload**:  
  - `data.get("q_organization_job_titles") or data.get("organization_job_titles")`  
  - Split, strip: list banake `payload["q_organization_job_titles"] = org_job_titles`  
  - Apollo: companies jahan yeh job titles exist karte hain (organization-level).

### 3.11 Organization Job Locations
- **Form**: `organization_job_locations` (CharField, comma-separated).
- **Payload**:  
  - List banake `payload["organization_job_locations"] = job_locs`  
  - Apollo: jobs in locations mein (e.g. "lahore", "karachi").

### 3.12 Lookalike Organization IDs
- **Form**: `lookalike_organization_ids` (CharField, comma-separated IDs).
- **Payload**:  
  - List of IDs: `payload["lookalike_organization_ids"] = lookalike_ids`  
  - Apollo: "lookalike" in organizations ke hisaab se similar companies.

### 3.13 Pagination (Page & Per page)
- **Form**: `page` (int, default 1), `per_page` (choice: 10, 25, 50, 100).
- **Payload**:  
  - `payload["page"] = page` (1-based).  
  - `payload["per_page"] = per_page` (max 100 in code).  
  - Apollo: kaun sa page aur kitne results per page.

---

## 4. Apollo Service (apollo_service.py)

### search_companies(payload)
```python
def search_companies(payload: dict) -> dict:
    headers = _get_headers()   # X-Api-Key from APOLLO_API_KEY
    r = _post_with_retry(APOLLO_COMPANY_SEARCH_URL, payload, headers)
    return r.json()
```
- **URL**: `https://api.apollo.io/api/v1/mixed_companies/search`
- **Method**: POST  
- **Headers**: `Content-Type: application/json`, `X-Api-Key: <APOLLO_API_KEY>`  
- **Body**: wahi `payload` jo `build_apollo_payload(data)` ne banaya.  
- **Response**: JSON with `accounts`, `organizations`, `pagination` (page, per_page, total_entries, total_pages), `breadcrumbs`, etc.

### Timeout & retries
- `DEFAULT_TIMEOUT = 120` (env se `APOLLO_REQUEST_TIMEOUT` se override).  
- `_post_with_retry`: read/connect timeout pe 2 retries, 2 sec wait.

---

## 5. End-to-end flow (ek line mein)

1. **HTML**: User form fill karke "Search Companies" dabata hai → POST same URL pe, `request.POST` + CSRF.  
2. **View**: `CompanySearchForm(request.POST)` → `cleaned_data`. Location hai to `per_page=100`, `page=1`.  
3. **Payload**: `build_apollo_payload(data)` → har filter (name, domains, locations, employees, revenue, keyword, industries, job titles/locations, lookalike, page, per_page) Apollo ke keys mein map.  
4. **API**: `search_companies(payload)` → POST `mixed_companies/search`, response mein `accounts` + `organizations` + `pagination`.  
5. **Merge**: Pehle page ki accounts + organizations merge; location filter + multi-page hone pe page 2, 3 bhi fetch karke merge.  
6. **Normalize**: `normalize_companies(accounts)` → common shape (id, name, domain, location fields, searchable_location_string, revenue, etc.).  
7. **Filter/Count**: Multi-page merge hone pe sab dikhao; nahi to location filter laga ke count; bina location ke `total_entries`.  
8. **Template**: `companies` + `total_count` → table mein saari rows render.

Is doc ke hisaab se tum har filter ko HTML field → view → `build_apollo_payload` → Apollo key trace kar sakte ho.
