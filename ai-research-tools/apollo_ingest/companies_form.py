from django import forms


# Apollo industry tags: (value=id, name=display). API filters[] options use these IDs.
INDUSTRIES_LIST = [
    ("5567e27c7369642ade490000", "alternative medicine"),
    ("5567e36f73696431a4970000", "animation"),
    ("5567cd82736964540d0b0000", "apparel & fashion"),
    ("5567cdb77369645401080000", "architecture & planning"),
    ("5567cd4d73696439d9030000", "arts & crafts"),
    ("5567cdf27369644cfd800000", "automotive"),
    ("5567e0dd73696416d3c20100", "aviation & aerospace"),
    ("5567ce237369644ee5490000", "banking"),
    ("5567d08e7369645dbc4b0000", "biotechnology"),
    ("5567e0f973696416d34e0200", "broadcast media"),
    ("5567e1a17369641ea9d30100", "building materials"),
    ("5567e0fa73696410e4c51200", "business supplies & equipment"),
    ("5567cdb773696439a9080000", "capital markets"),
    ("5567e21e73696426a1030000", "chemicals"),
    ("5567cdda7369644eed130000", "civic & social organization"),
    ("5567e13a73696418756e0200", "civil engineering"),
    ("5567e1887369641d68d40100", "commercial real estate"),
    ("5567cd877369644cf94b0000", "computer & network security"),
    ("5567cd8b736964540d0f0000", "computer games"),
    ("5567e0d47369641233eb0600", "computer hardware"),
    ("5567cdbe7369643b78360000", "computer networking"),
    ("5567cd4e7369643b70010000", "computer software"),
    ("5567cd4773696439dd350000", "construction"),
    ("5567e1947369641ead570000", "consumer electronics"),
    ("5567ce987369643b789e0000", "consumer goods"),
    ("5567d1127261697f2b1d0000", "consumer services"),
    ("5567e1ae73696423dc040000", "cosmetics"),
    ("5567e8a27369646ddb0b0000", "dairy"),
    ("5567e1097369641b5f810500", "defense & space"),
    ("5567cdbc73696439d90b0000", "design"),
    ("5567cd4c73696453e1300000", "higher education"),
    ("5567cdde73696439812c0000", "hospital & health care"),
    ("5567ce9d7369643bc19c0000", "hospitality"),
    ("5567e0e37369640e5ac10c00", "human resources"),
    ("5567ce9d7369645430c50000", "import & export"),
    ("5567d02b7369645d8b140000", "individual & family services"),
    ("5567e1337369641ad2970000", "industrial automation"),
    ("5567e0c97369640d2b3b1600", "information services"),
    ("5567cd4773696439b10b0000", "information technology & services"),
    ("5567cdd973696453d93f0000", "insurance"),
    ("5567e3657369642f4ec90000", "international affairs"),
    ("5567ce9c7369644eed680000", "international trade & development"),
    ("5567cd4d736964397e020000", "internet"),
    ("5567e1ab7369641f6d660100", "investment banking"),
    ("5567e0bc7369641d11550200", "investment management"),
    ("55680a8273696407b61f0000", "judiciary"),
    ("5567e0e073696408da441e00", "law enforcement"),
    ("5567cd4d7369644d513e0000", "printing"),
    ("5567cd49736964541d010000", "professional training & coaching"),
    ("5567e2907369642433e60200", "program development"),
    ("5567e28a7369642ae2500000", "public policy"),
    ("5567ce5973696453d9780000", "public relations & communications"),
    ("5567cd4a7369643ba9010000", "public safety"),
    ("5567ce5b73696439a17a0000", "publishing"),
    ("5567e14673696416d38c0300", "railroad manufacture"),
    ("5567fd5a73696442b0f20000", "ranching"),
    ("5567cd477369645401010000", "real estate"),
    ("5567e134736964214f5e0000", "recreational facilities & services"),
    ("5567e0f27369640e5aed0c00", "religious institutions"),
    ("5567cd49736964540d020000", "renewables & environment"),
    ("5567e09f736964160ebb0100", "research"),
    ("5567e0e0736964198de70700", "restaurants"),
    ("5567ced173696450cb580000", "retail"),
    ("5567e19b7369641ead740000", "security & investigations"),
    ("5567e0d87369640e5aa30c00", "semiconductors"),
]

# Seniority choices for Apollo API
SENIORITY_CHOICES = [
    ("owner", "Owner"),
    ("founder", "Founder"),
    ("c_suite", "C-Suite"),
    ("partner", "Partner"),
    ("vp", "VP"),
    ("head", "Head"),
    ("director", "Director"),
    ("manager", "Manager"),
    ("senior", "Senior"),
    ("entry", "Entry"),
    ("intern", "Intern"),
]

# Job title values from Apollo person_title tags – sent as person_titles[] to mixed_people api_search
JOB_TITLE_CHOICES = [
    ("manager", "Manager"),
    ("project manager", "Project Manager"),
    ("teacher", "Teacher"),
    ("owner", "Owner"),
    ("student", "Student"),
    ("director", "Director"),
    ("software engineer", "Software Engineer"),
    ("consultant", "Consultant"),
    ("account manager", "Account Manager"),
    ("engineer", "Engineer"),
    ("professor", "Professor"),
    ("sales manager", "Sales Manager"),
    ("sales", "Sales"),
    ("partner", "Partner"),
    ("associate", "Associate"),
    ("president", "President"),
    ("administrative assistant", "Administrative Assistant"),
    ("supervisor", "Supervisor"),
    ("general manager", "General Manager"),
    ("realtor", "Realtor"),
]


class CompanySearchForm(forms.Form):
    """Form for searching companies with Apollo API filters."""

    # Company name search
    company_name = forms.CharField(
        required=False,
        label="Company Name",
        widget=forms.TextInput(attrs={"placeholder": "e.g., Google, Microsoft"}),
    )

    # Domains (comma separated)
    domains = forms.CharField(
        required=False,
        label="Domains",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g., google.com, microsoft.com"}
        ),
    )

    # Locations - included
    locations_included = forms.CharField(
        required=False,
        label="Locations (Include)",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g., United States, Germany, London"}
        ),
    )

    # Locations - not included
    locations_excluded = forms.CharField(
        required=False,
        label="Locations (Exclude)",
        widget=forms.TextInput(attrs={"placeholder": "e.g., China, Russia"}),
    )

    # Employee range - min
    employees_min = forms.IntegerField(
        required=False,
        label="Employees Min",
        min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "e.g., 10"}),
    )

    # Employee range - max
    employees_max = forms.IntegerField(
        required=False,
        label="Employees Max",
        widget=forms.NumberInput(attrs={"placeholder": "e.g., 500"}),
    )

    # Industries (multi-select) – value=Apollo industry id, sent as filters[].options (id array)
    industries = forms.MultipleChoiceField(
        required=False,
        choices=INDUSTRIES_LIST,
        label="Industries (include)",
        widget=forms.SelectMultiple(attrs={"size": "5"}),
    )

    # Industries to exclude – same id list, sent as filters[].options (id array)
    industries_exclude = forms.MultipleChoiceField(
        required=False,
        choices=INDUSTRIES_LIST,
        label="Industries (exclude)",
        widget=forms.SelectMultiple(attrs={"size": "3"}),
    )

    # Organization job titles (company search filter)
    organization_job_titles = forms.CharField(
        required=False,
        label="Org job titles",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g., software, engineer (comma-separated)"}
        ),
    )

    # Organization job locations (company search filter)
    organization_job_locations = forms.CharField(
        required=False,
        label="Org job locations",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g., lahore, karachi (comma-separated)"}
        ),
    )

    # Lookalike organization IDs (optional)
    lookalike_organization_ids = forms.CharField(
        required=False,
        label="Lookalike org IDs",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g., 57c4ace7a6da9867ee5599e7 (comma-separated)"}
        ),
    )

    # Revenue range - min (in millions)
    revenue_min = forms.IntegerField(
        required=False,
        label="Revenue Min ($M)",
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "e.g., 1"}),
    )

    # Revenue range - max (in millions)
    revenue_max = forms.IntegerField(
        required=False,
        label="Revenue Max ($M)",
        widget=forms.NumberInput(attrs={"placeholder": "e.g., 100"}),
    )

    # Organization keyword tags (for company search)
    organization_keyword = forms.CharField(
        required=False,
        label="Organization Keyword",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g., caster, software (comma-separated)"}
        ),
    )

    # Pagination (for company search results)
    page = forms.IntegerField(
        required=False,
        initial=1,
        min_value=1,
        label="Page",
        widget=forms.NumberInput(attrs={"placeholder": "1", "min": "1"}),
    )
    per_page = forms.TypedChoiceField(
        required=False,
        initial=25,
        coerce=int,
        choices=[(10, "10"), (25, "25"), (50, "50"), (100, "100")],
        label="Per page",
    )

    # Job titles (multi-select) — used for people/contacts search only, not sent to company search
    job_titles = forms.MultipleChoiceField(
        required=False,
        choices=JOB_TITLE_CHOICES,
        label="Job Titles",
        widget=forms.SelectMultiple(attrs={"size": "5"}),
    )

    # Seniorities (multi-select)
    seniorities = forms.MultipleChoiceField(
        required=False,
        choices=SENIORITY_CHOICES,
        label="Seniorities",
        widget=forms.SelectMultiple(attrs={"size": "5"}),
    )
