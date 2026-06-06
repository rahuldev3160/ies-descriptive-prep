"""Replace 5 closed analytical essay prompts with open-ended thesis-driven topics."""

DB = "ies"

_ESSAYS = [
    {
        "question_id": "eng_essay_001",
        "source_exam": "upsc_ies_style",
        "difficulty": "medium",
        "prompt_text": (
            "India's informal economy employs nearly 90% of its workforce yet contributes less than 50% of GDP. "
            "Is it a structural problem to be solved, or a strength to be harnessed?\n\n"
            "Write an essay of approximately 500 words. A clear title is required.\n"
            "(UPSC / IES General English — Essay)"
        ),
        "intro_text": (
            "The Hidden Engine: India's Informal Economy as Asset and Liability\n\n"
            "India's informal economy — millions of street vendors, home weavers, agricultural labourers, "
            "and roadside mechanics — is routinely cast as evidence of developmental failure: unregulated, "
            "unprotected, and unproductive. Yet this framing misses an inconvenient truth. The informal "
            "sector has sustained hundreds of millions precisely because formal institutions did not reach "
            "them. The question of whether it constitutes a problem to be solved or a strength to be "
            "harnessed is therefore not rhetorical — it carries real consequences for policy design."
        ),
        "body_text": (
            "The case for the informal economy as strength rests on its demonstrated resilience and "
            "adaptive capacity. Small informal enterprises serve markets that formal businesses find "
            "unprofitable — remote villages, ultra-low-income households, niche cultural goods. During "
            "COVID-19 lockdowns and the 2016 demonetisation shock, informal networks of mutual credit "
            "and barter sustained communities where formal supply chains collapsed. The flexibility that "
            "makes informality legally precarious is also what makes it economically durable.\n\n"
            "Yet romanticising informality carries a steep human cost. Informal workers have no access "
            "to Employees' State Insurance, Employees' Provident Fund, or formal credit — leaving them "
            "exposed to health shocks and old-age poverty. The productivity gap is not cosmetic: the "
            "same worker in a formal enterprise produces significantly more than their informal "
            "counterpart, because formal firms invest in training, machinery, and quality systems that "
            "the informal sector cannot afford. Child labour and wage theft persist where enforcement "
            "does not reach.\n\n"
            "Attempts to forcibly accelerate formalisation have repeatedly backfired. Demonetisation "
            "targeted informal cash transactions and destroyed livelihoods before any formal alternative "
            "existed. The lesson is that formalisation must be led by opportunity, not coercion — made "
            "attractive rather than compulsory. India's e-Shram portal, which registered 280 million "
            "informal workers by 2024 without immediately imposing compliance costs, points toward this "
            "middle path: recognition without forced transition.\n\n"
            "The productive synthesis lies in building bridges. Cash-flow-based digital credit, enabled "
            "by UPI and GST transaction histories, extends formal financing to enterprises that cannot "
            "post collateral. Portable social protection — health and pension coverage that follows "
            "workers regardless of employer — offers informally employed people the security of "
            "formality without demanding they cross into it. These are policies that harness the "
            "informal economy's scale while progressively closing its welfare gaps."
        ),
        "conclusion_text": (
            "India's informal economy is neither purely a strength nor a problem awaiting a solution. "
            "It is an ecosystem that arose where formal institutions failed to reach, and it will "
            "retreat only when those institutions become more accessible than informal alternatives. "
            "The policy imperative is not to suppress informality but to make formality genuinely "
            "worthwhile — cheaper to enter, richer in protection, and honest about the transition "
            "costs for those who make the crossing. That is harnessing, not solving."
        ),
    },
    {
        "question_id": "eng_essay_002",
        "source_exam": "upsc_ies_style",
        "difficulty": "medium",
        "prompt_text": (
            "'Growth without equity is not development.' "
            "Critically examine this statement in the context of India's economic experience.\n\n"
            "Write an essay of approximately 500 words. A clear title is required.\n"
            "(UPSC / IES General English — Essay)"
        ),
        "intro_text": (
            "Growth and Justice: Why Numbers Are Not Enough\n\n"
            "Economic growth — measured by GDP expansion — has long served as the primary metric of "
            "national progress. Yet the proposition that growth divorced from equity does not constitute "
            "genuine development challenges this conflation. In India, decades of high growth rates "
            "coexisting with persistent hunger, illiteracy, and human deprivation make this argument "
            "more than philosophical. It is a question about what development is actually for."
        ),
        "body_text": (
            "India's post-liberalisation growth record illustrates the limits of the GDP lens. Between "
            "1991 and 2015, India averaged 6.5% annual growth while remaining home to the world's "
            "largest concentration of extreme poverty. The Human Development Index in 2023 placed India "
            "134th of 193 countries — below countries with significantly lower per capita incomes. "
            "The Global Hunger Index placed India 105th of 125 nations the same year. These are not "
            "marginal oversights; they are evidence that rising national income does not automatically "
            "translate into rising human welfare when the pattern of growth concentrates gains at the top.\n\n"
            "Amartya Sen's critique — that development must be understood as the expansion of human "
            "freedoms rather than the accumulation of wealth — gives this observation a theoretical "
            "grounding. A person who earns ₹2,000 a month but cannot read, access healthcare, or "
            "protect themselves from arbitrary eviction is not meaningfully more developed than one "
            "who earned ₹500 a month in 1980. Development requires capability, not merely income.\n\n"
            "Yet growth's contribution to equity cannot be dismissed. The dramatic reduction in "
            "extreme poverty since 1991 — from over 45% by the ₹2.15/day measure to under 13% by "
            "2019 — was not achieved despite growth but because of it. Government revenues generated "
            "by growth fund the MGNREGS, PM-KISAN, and public health infrastructure that constitute "
            "the equity-building machinery of the state. Without growth, redistribution consumes "
            "capital rather than expanding it.\n\n"
            "The resolution of this apparent tension lies not in choosing between growth and equity "
            "but in asking what kind of growth. Labour-intensive manufacturing growth — the path "
            "East Asia followed between 1960 and 2000 — spreads gains widely through employment. "
            "Capital-intensive services growth, which India has disproportionately relied upon, "
            "concentrates them among the skilled. India's development challenge is to build growth "
            "engines — in labour-intensive manufacturing, agricultural value chains, and the rural "
            "non-farm economy — where equity is a structural outcome of the process, not a remedial afterthought."
        ),
        "conclusion_text": (
            "Growth without equity is not development — but neither is equity without growth. "
            "The real policy question is whether the pattern of growth is inherently inclusive or "
            "whether redistribution must perpetually fight the market's tendency toward concentration. "
            "India's task is to design the former: growth through sectors and institutional arrangements "
            "that make wide participation the condition of success, not a charitable add-on. "
            "Only then does economic progress become the same thing as human development."
        ),
    },
    {
        "question_id": "eng_essay_003",
        "source_exam": "upsc_ies_style",
        "difficulty": "hard",
        "prompt_text": (
            "Technology has been described as the great equaliser of our time. "
            "Critically examine whether this is true for India.\n\n"
            "Write an essay of approximately 500 words. A clear title is required.\n"
            "(UPSC / IES General English — Essay)"
        ),
        "intro_text": (
            "The Digital Divide: Equaliser or Amplifier?\n\n"
            "The claim that technology democratises opportunity is intuitively compelling. A smartphone "
            "gives a farmer in Vidarbha access to the same market prices as a commodity broker in Mumbai; "
            "an Aadhaar number gives a migrant worker access to welfare benefits regardless of geography. "
            "Yet for every story of digital empowerment, there is a counter-narrative of exclusion, "
            "surveillance, and structural advantage amplified by access gaps. Whether technology "
            "equalises or divides depends critically on who has access, what they can do with it, "
            "and who controls the infrastructure."
        ),
        "body_text": (
            "India's digital stack has produced genuine equalising outcomes. UPI has enabled over "
            "500 million smartphone users to transact at near-zero cost, removing the economic advantage "
            "that formal bank account holders once held over cash-dependent informal workers. Direct "
            "Benefit Transfer has delivered over ₹34 lakh crore in welfare payments, bypassing "
            "intermediaries who historically captured a significant share of public spending intended "
            "for the poor. Agricultural price platforms have improved market transparency for farmers, "
            "narrowing the information asymmetry with traders.\n\n"
            "Yet technology's equalising power depends on a prior condition — access — that is itself "
            "distributed unequally. Rural internet penetration remains below 40%; smartphone ownership "
            "among the bottom income quintile is under 20%. The digital economy's largest gains — in "
            "IT services, platform employment, and fintech — have overwhelmingly accrued to educated "
            "urban workers. The gig economy, celebrated as democratised entrepreneurship, offers "
            "flexibility without social protection: a new layer of precarious labour at the base of "
            "the technology-enabled economy.\n\n"
            "Deeper than the access gap is the ownership gap. India's digital infrastructure is "
            "dominated by a handful of large platforms whose network effects concentrate power at the "
            "top. The more users a platform accumulates, the less viable competition becomes — meaning "
            "that gains from India's digital economy are increasingly intermediated by a small number "
            "of gatekeepers, regardless of how widely basic connectivity spreads. The Digital Personal "
            "Data Protection Act 2023 and Open Network for Digital Commerce represent institutional "
            "attempts to build the conditions for genuine equalisation, but their implementation "
            "is nascent.\n\n"
            "Technology's equalising potential is also threatened by the automation it enables. "
            "AI is displacing the cognitive, routine-service tasks — data entry, customer support, "
            "basic code review — in which India's mid-skilled urban workforce has built its "
            "comparative advantage. If the jobs that automation creates require education that the "
            "school system does not reliably provide, digital technology will deepen the divide "
            "between the globally connected elite and the informally employed majority."
        ),
        "conclusion_text": (
            "Technology is neither inherently equalising nor inherently divisive — it is a force "
            "multiplier that amplifies the capabilities of those who have access and the structural "
            "advantages of those who own infrastructure. Whether it equalises India depends on "
            "political choices: universal connectivity, data rights for citizens, open platform "
            "standards, and education systems that build the foundational skills the digital "
            "economy demands. The technology to equip every citizen equally exists. "
            "What remains uncertain is whether the will to ensure it does will follow."
        ),
    },
    {
        "question_id": "eng_essay_004",
        "source_exam": "upsc_ies_style",
        "difficulty": "medium",
        "prompt_text": (
            "Environmental sustainability and economic development are compatible, not contradictory, "
            "goals for India. Do you agree?\n\n"
            "Write an essay of approximately 500 words. A clear title is required.\n"
            "(UPSC / IES General English — Essay)"
        ),
        "intro_text": (
            "Green and Growing: The False Dilemma of Sustainability and Development\n\n"
            "The framing of development and environment as opposing forces — where growth requires "
            "resource extraction and pollution while sustainability requires restraint — has deep "
            "roots in industrial history. But this may be a legacy of 20th-century technologies, "
            "not a universal truth. For India, simultaneously aspiring to high economic growth and "
            "managing severe climate vulnerabilities, the question of whether sustainability and "
            "development can coexist is not academic. The answer determines the investment patterns, "
            "energy choices, and industrial policies that will shape the lives of hundreds of millions."
        ),
        "body_text": (
            "The tension is real and should not be minimised. India's per capita energy consumption "
            "remains among the lowest in the G20; electrification, industrialisation, and urbanisation "
            "— the processes through which incomes rise — have historically tracked with rising "
            "emissions. Coal provides over 70% of India's electricity, and a rapid energy transition "
            "imposes real costs on affordable industrial power, factory viability, and employment in "
            "coal-belt communities. Dismissing these costs as temporary adjustment friction understates "
            "their human weight.\n\n"
            "Yet the framework of incompatibility assumes that only one development path exists: the "
            "carbon-intensive one that Europe and America took in the 19th and 20th centuries. India "
            "has the advantage of a late start. Solar generation costs have fallen 90% since 2010; "
            "India's installed solar capacity exceeded 90 GW in 2024, now cost-competitive with "
            "coal-based generation without subsidy. Investment in climate-resilient agriculture, "
            "energy-efficient buildings, and mass urban transit generates employment and productivity "
            "gains — these are not alternatives to growth but forms of it.\n\n"
            "The calculation also runs the other way: the development cost of failing to invest in "
            "sustainability is increasingly large and certain. Extreme heat events already reduce "
            "agricultural output and outdoor labour productivity by measurable amounts. The RBI's "
            "Financial Stability Report 2023 flagged significant agricultural output risk attributable "
            "to climate variability. Coastal flooding, water scarcity, and glacial retreat impose "
            "infrastructure and welfare costs that compound the burden on fiscal resources. "
            "Unsustainable development is not free development — it borrows against a future "
            "that must repay the debt.\n\n"
            "The compatible path requires three institutional foundations: pricing carbon so that "
            "market decisions reflect environmental costs; directing capital toward green infrastructure "
            "through sovereign green bonds and climate-aligned bank lending; and ensuring that transition "
            "costs do not fall disproportionately on coal-region workers and energy-poor households "
            "through targeted social protection and just transition programmes."
        ),
        "conclusion_text": (
            "Sustainability and development are not the same goal — but they are not opposing forces "
            "either. They are complementary constraints that, if internalised into planning, produce "
            "a more durable and equitable form of growth. India cannot afford to develop "
            "unsustainably — the climate costs are already arriving. It also cannot afford to be "
            "sustainable without developing — the human cost of poverty is too immediate and too large. "
            "The task is not to choose between them but to build the institutions and incentives "
            "that make the two paths converge."
        ),
    },
    {
        "question_id": "eng_essay_005",
        "source_exam": "upsc_ies_style",
        "difficulty": "hard",
        "prompt_text": (
            "Automation and artificial intelligence will create more opportunities than they destroy "
            "for Indian workers. Do you agree?\n\n"
            "Write an essay of approximately 500 words. A clear title is required.\n"
            "(UPSC / IES General English — Essay)"
        ),
        "intro_text": (
            "The Automation Question: India's Workforce at a Crossroads\n\n"
            "Few questions carry more consequence for India's development trajectory than what "
            "automation means for its workforce. With 450 million workers in informal employment, "
            "9 million new labour market entrants annually, and AI platforms displacing routine "
            "cognitive tasks at unprecedented speed, the stakes of getting the answer right could "
            "not be higher. Whether automation creates or destroys opportunity for Indian workers "
            "depends less on the technology itself than on the education, policy, and institutional "
            "environment into which it is introduced."
        ),
        "body_text": (
            "The optimistic case draws on historical precedent. Every previous wave of technological "
            "displacement — from handlooms to steam power, from telegraphs to computers — ultimately "
            "generated more jobs than it destroyed, through higher productivity, lower prices, and "
            "entirely new categories of economic activity. In India, the IT sector — itself an "
            "automation-enabling industry — employs over 5 million workers directly. Platform-based "
            "gig work has created income opportunities for drivers, delivery workers, and freelancers "
            "who had no viable formal employment alternative.\n\n"
            "The pessimist case notes that historical analogies may mislead. Previous technological "
            "transitions unfolded over decades, allowing labour markets to absorb displacement "
            "gradually. AI is compressing this timeline: tasks that once required years to automate "
            "now require months. India's service sector — the engine of post-liberalisation growth "
            "— faces particular exposure: customer service, data entry, and basic IT support, which "
            "employ millions of mid-skilled workers, are already being displaced by large language "
            "models. Unlike previous transitions, this one targets cognitive work — precisely the "
            "comparative advantage India has built.\n\n"
            "Beyond displacement, there is a structural human capital constraint. The jobs that "
            "automation creates — AI trainers, robotics engineers, data architects — require "
            "foundational and higher education that India's school system does not yet reliably "
            "produce. ASER 2023 found that 25% of Class 8 students cannot read a Class 2-level "
            "paragraph. If learning outcomes do not improve rapidly, the new opportunities that "
            "automation creates will accrue to the globally connected educated elite, while the "
            "informally employed majority faces displacement without viable alternatives.\n\n"
            "The policy response must build the absorptive capacity — through education, skilling, "
            "and social protection — that determines which side of this transition India falls on. "
            "The National Apprenticeship Promotion Scheme, PM Kaushal Vikas Yojana, and portable "
            "social protection for gig workers are the institutional foundations for this response; "
            "their scale and quality require urgent upgrading."
        ),
        "conclusion_text": (
            "Automation will create and destroy opportunity simultaneously — the balance is not "
            "fixed by technology but determined by policy choices. For a country with 9 million "
            "new workers annually, a learning crisis at the foundation level, and inadequate "
            "social protection, the optimistic scenario is available but not automatic. "
            "A workforce cannot be routed into new jobs by market forces alone when the education "
            "system has not yet equipped it with the skills those jobs require. The future of work "
            "in India will be shaped by the investments made today — in learning, in institutions, "
            "and in the political will to treat the workforce as a national asset rather than "
            "an economic variable."
        ),
    },
]


def run(conn):
    for q in _ESSAYS:
        conn.execute(
            "UPDATE english_questions "
            "SET prompt_text=?, intro_text=?, body_text=?, conclusion_text=?, source_exam=?, difficulty=? "
            "WHERE question_id=? AND exam_id='english_practice'",
            (
                q["prompt_text"], q["intro_text"], q["body_text"],
                q["conclusion_text"], q["source_exam"], q["difficulty"],
                q["question_id"],
            ),
        )
    conn.commit()
