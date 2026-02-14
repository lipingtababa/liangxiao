# MySQL vs PostgreSQL: Alternative Perspectives

*Beyond the "obedience test" narrative and the "suite thesis" - what OTHER frameworks explain MySQL's past dominance and PostgreSQL's current rise?*

---

## 1. Corporate Trust & Open Source Governance

💡 **Oracle Acquisition Created Distrust (2010)**

**The Event:**
- MySQL AB acquired by Sun Microsystems (2008)
- Sun acquired by Oracle Corporation (2010)
- Community feared Oracle would let MySQL stagnate to protect commercial Oracle DB

**The Impact:**
- MySQL users "wary" and "at a loss for words" when Oracle acquired
- At least one organization migrated 34 core MySQL databases to PostgreSQL
- BUT: Many forked to MariaDB instead of switching to PostgreSQL
- MySQL's original founder (Michael Widenius) left and created MariaDB in 2009

**Why Interesting:**
PostgreSQL benefited from Oracle distrust, but so did MariaDB. Question: Why did some go PostgreSQL vs MariaDB? Different risk profiles? MariaDB = MySQL-compatible fork (easy migration), PostgreSQL = different architecture (more disruption).

**Sources:**
- http://jeremy.zawodny.com/blog/archives/011386.html
- https://www.tecmint.com/the-story-behind-acquisition-of-mysql-and-the-rise-of-mariadb/
- https://www.informationweek.com/it-sectors/mysql-users-wary-on-oracle-acquisition

---

## 2. Licensing Economics: GPL vs BSD

💡 **PostgreSQL is "More Free" for Commercial Software**

**The Difference:**
- **MySQL**: GNU GPL-2 license
  - If you embed MySQL in proprietary software sold to customers, you need commercial license
  - MySQL Standard Edition: ~$2,000/server/year
  - MySQL Enterprise Edition: ~$5,000/server/year
  - Only free if used internally or in open-source software

- **PostgreSQL**: BSD-style permissive license
  - Can embed in closed-source products without releasing source code
  - No license fees ever, regardless of use case

**Why Interesting:**
For SaaS companies and ISVs selling proprietary software, PostgreSQL is genuinely "more free" than MySQL. This isn't about features or ecosystem - it's legal/financial risk. Companies building commercial products face hidden MySQL costs that don't exist with PostgreSQL.

**Sources:**
- https://www.getgalaxy.io/learn/glossary/how-to-navigate-the-mysql-open-source-license-in-postgresql
- https://medium.com/version-1/mysql-licensing-explained-d696460f8bf0
- https://news.ycombinator.com/item?id=25932194

---

## 3. The Talent Market Economics

💡 **PostgreSQL DBAs Earn Nearly 2x MySQL DBAs**

**The Numbers (2024-2025):**
- PostgreSQL DBAs: Average $132,801/year
- MySQL DBAs: Average $73,281/year
- Nearly 2x salary difference!

**Why Interesting:**
Creates powerful incentive for DBAs to specialize in PostgreSQL rather than MySQL. Could create talent shortage for MySQL, making PostgreSQL more attractive to companies (easier to hire skilled DBAs). Also signals market perception: PostgreSQL skills are valued higher.

**But also consider:**
- Could reflect supply/demand (fewer PostgreSQL DBAs = higher wages)
- Or PostgreSQL DBAs work at higher-paying companies (tech startups vs WordPress shops)
- Correlation vs causation

**Sources:**
- https://www.payscale.com/research/US/Job=Senior_Database_Administrator_(DBA)/Salary/57191da8/PostgreSQL
- https://www.ziprecruiter.com/Salaries/Mysql-Administrator-Salary
- https://www.refontelearning.com/salary-guide/database-administration-salary-suide-2025

---

## 4. WordPress Lock-in: The Installed Base Anchor

💡 **WordPress Powers 40%+ of Websites, MySQL-Only Forever**

**The Reality:**
- WordPress officially only supports MySQL/MariaDB
- Cannot officially support PostgreSQL due to:
  - Plugin ecosystem depends on MySQL-specific functions
  - Testing every WordPress version against PostgreSQL too costly
  - Many queries cannot be expressed in database-agnostic way
  - Core architecture not built for pluggable database backends

**Why Interesting:**
While NEW projects shift to PostgreSQL, the EXISTING web (WordPress-dominated) is permanently MySQL. PostgreSQL's growth might be entirely in new applications, not migration of old ones. This explains MySQL's continued large installed base despite PostgreSQL "winning" new mindshare.

**The Paradox:**
- PostgreSQL is "winning" the future
- But MySQL owns the past (and present installed base)
- WordPress alone keeps MySQL alive regardless of technical merit

**Sources:**
- https://codex.wordpress.org/Using_Alternative_Databases
- https://visualmodo.com/postgresql-vs-mysql-for-wordpress-how-they-compare/
- https://www.fobwp.com/wordpress-and-postgresql-guide/

---

## 5. The "Boring Technology" Philosophy

💡 **Dan McKinley's "Choose Boring Technology" Favored MySQL... But When Did PostgreSQL Become "Boring"?**

**The Philosophy:**
- Dan McKinley (Etsy): Use "innovation tokens" sparingly
- Boring technology = familiar, well-established, well-tested, widely adopted
- MySQL as canonical example of "boring" tech
- DynamoDB vs MySQL costs an "innovation token"
- When Etsy consolidated onto PHP, MySQL, Memcached, Gearman - everything "just worked" as they scaled 20x

**The Paradox:**
- MySQL benefited from being "boring/safe" choice in 2010s
- BUT PostgreSQL is equally old (first released 1996, same era as MySQL 1995)
- When did PostgreSQL stop being "innovative" and become "boring"?
- The "boring" label is **culturally constructed**, not objectively measured by age

**Why Interesting:**
"Boring technology" became a meme that reinforced MySQL's position. But the label is subjective and shifts over time. PostgreSQL is now arguably just as "boring" (proven, stable, 35+ years old) but still carries "innovative" perception. Shows how narratives outlive technical reality.

**Sources:**
- https://mcfunley.com/choose-boring-technology
- https://www.annageller.com/p/summary-choose-boring-technology
- https://www.brethorsting.com/blog/2025/07/choose-boring-technology,-revisited/

---

## 6. Migration Lock-in and Switching Costs

💡 **Why Companies Can't Leave MySQL Even When They Want To**

**The Economics of Migration:**
- Gartner: Only 17% of data migrations complete within budget/timeline
- Average cost overrun: 30%
- 4 hours downtime = $20k lost revenue + $8k productivity loss (for $10M/year business)
- True zero-downtime migration is "impossible"

**Technical Risks:**
- Data type incompatibilities between MySQL and PostgreSQL
- Constraint behavior differences
- Performance characteristics change
- Incomplete backup strategies prevent recovery from failed migrations

**Why Companies Don't Switch:**
- "Most teams underestimate what's involved"
- Not just technical switch - architecture, downtime, tooling, testing, business continuity
- Database migrations are "business continuity challenges requiring comprehensive risk management"

**Why Interesting:**
MySQL's dominance is partially explained by **switching costs**, not current merit. Companies KNOW PostgreSQL might be better but can't justify migration risk/cost. This is "technical debt at the database level." MySQL persists through inertia, not choice.

**Sources:**
- https://airbyte.com/data-engineering-resources/risks-migrating-mysql-to-postgresql
- https://www.ispirer.com/blog/real-cost-of-database-migration
- https://www.percona.com/blog/best-practices-for-postgresql-migration/
- https://www.astera.com/type/blog/data-migration-challenges/

---

## 7. The Stack Overflow Paradox

💡 **MySQL Has 5x More Questions, But PostgreSQL Is "Most Admired"**

**The Numbers:**
- Stack Overflow has **5x more questions** for MySQL than PostgreSQL
- MySQL has wider range of documentation, books, community resources
- MySQL market share (deployment) is 6x higher than PostgreSQL

**BUT:**
- PostgreSQL is now "most popular" database in Stack Overflow surveys (2023-2024)
- PostgreSQL is "most admired" and "most desired" database
- PostgreSQL usage: 33% (2018) → 49% (2024), now exceeding MySQL

**Why Interesting:**
MySQL's larger Q&A base is a **lagging indicator** of OLD dominance, not current preference. Two interpretations:

1. **Optimistic**: PostgreSQL has fewer questions because it works better (fewer edge cases, bugs, gotchas)
2. **Realistic**: MySQL's installed base generates ongoing questions, while PostgreSQL has momentum in new projects

Classic "installed base vs momentum" situation.

**Sources:**
- https://stormatics.tech/blogs/a-look-at-postgresqls-journey-over-5-years-in-stack-overflows-developer-survey
- https://www.keboola.com/blog/postgresql-vs-mysql
- https://survey.stackoverflow.co/2024/

---

## 8. Decision Fatigue and Cognitive Load

💡 **Developers Choose Defaults When Mentally Exhausted**

**The Psychology:**
- Decision fatigue: making many choices depletes mental energy
- Developers introduce subtle bugs due to "fatigued judgment calls"
- When cognitively depleted, people rely on **default options** to save mental energy
- More than 12 decision points causes slower response times and abandonment

**Application to Databases:**
LAMP/Heroku/Vercel provide "sensible defaults" that reduce cognitive load. Choosing MySQL vs PostgreSQL isn't just about features - it's about **mental energy**.

**Why Interesting:**
Platforms that provide database as default choice reduce decision burden. This explains why suite integration works better than "best tool for the job" approach. Developers don't want to evaluate databases - they want to ship features. Defaults win.

**Counter-consideration:**
Is this "decision fatigue" or "rational efficiency"? Maybe developers SHOULD spend cognitive energy on important architecture decisions. But in practice, they're making hundreds of decisions per day.

**Sources:**
- https://www.monitask.com/en/business-glossary/decision-fatigue
- https://thedecisionlab.com/biases/decision-fatigue
- https://ramhee.com/the-psychology-of-digital-decision-fatigue/

---

## 9. THE PLOT TWIST: Uber Went PostgreSQL → MySQL (2016)

💡 **Not All Migrations Go Toward PostgreSQL!**

**The Story:**
Uber started with PostgreSQL during explosive growth phase (powerful, standards-compliant, strong reputation). But in 2016, Uber migrated FROM PostgreSQL TO MySQL.

**Why Uber Switched:**

1. **Write Amplification (MVCC Implementation)**
   - PostgreSQL UPDATE = DELETE + INSERT (leaves old row version in place)
   - Powerful for concurrency but expensive for write-heavy workloads

2. **Replication Differences**
   - MySQL replication binary log more compact than PostgreSQL WAL
   - MySQL replicas have true MVCC semantics (read queries don't block replication)

3. **Index Management**
   - PostgreSQL indexes reference physical row location (ctid)
   - When row updated, physical location changes, ALL indexes must update
   - Index bloat accumulates over time, slowing queries

4. **Upgrade Challenges**
   - Uber went from Postgres 9.1 → 9.2 successfully
   - But process took so many hours they "couldn't afford to do it again"
   - By time Postgres 9.3 released, dataset had grown substantially

**Why Interesting:**
This COMPLETELY CONTRADICTS the "PostgreSQL is winning" narrative! At scale, MySQL had advantages for Uber's specific write-heavy, rapidly growing workload. Reminds us database choice is **CONTEXT-DEPENDENT**, not absolute. PostgreSQL isn't universally better.

**Note:** Many criticized Uber's decision, saying they were using old Postgres version and techniques improved since then. But still: real companies make real trade-offs.

**Sources:**
- https://www.uber.com/blog/postgres-to-mysql-migration/
- https://medium.com/@karamalqinneh/postgresql-vs-mysql-diving-deep-into-ubers-migration-decision-ffa9441d7cb7
- https://medium.com/@mouhandalkadri/catching-up-with-the-past-reevaluating-ubers-postgresql-abandonment-in-the-era-of-modern-versions-79bd824be827

---

## 10. PostgreSQL's Real Weaknesses

💡 **PostgreSQL Isn't Objectively "Better" - Different Trade-offs**

**Acknowledged Limitations:**

1. **Horizontal Scaling**
   - PostgreSQL is "built to scale UP, not OUT"
   - No native horizontal scaling support
   - Needs extra tools (Citus, pgpool) for sharding
   - Increases deployment and management complexity

2. **Complexity and Configuration**
   - "Difficult to configure and maintain for high availability and optimal performance"
   - Steep learning curve for inexperienced users
   - Requires high degree of DBA/developer knowledge
   - Many advanced features require extensions not in base distribution

3. **Performance Trade-offs**
   - Slower than MySQL on read-heavy workloads
   - Extensive feature set causes higher latency in some cases
   - NOT designed well for large analytics/reporting queries (large table scans with few columns)

4. **Marketing and Adoption**
   - "Not owned by one organization, so trouble getting its name out there"
   - Changes for speed improvement require more work than MySQL
   - PostgreSQL focuses on compatibility over speed optimizations

**Why Interesting:**
MySQL has real advantages: simpler, faster for reads, easier horizontal sharding (Vitess), lower complexity. PostgreSQL's feature richness comes with trade-offs. Neither is objectively "better" - depends on workload, team skills, scale requirements.

**Sources:**
- https://www.ralantech.com/resources/postgresql-advantages-and-disadvantages/
- https://www.beekeeperstudio.io/blog/postgresql-limitations
- https://www.cockroachlabs.com/blog/limitations-of-postgres/
- https://medium.com/@ckolovson/weighing-the-pros-and-cons-of-postgresql-5a3603dd34ce

---

## Synthesis: Multiple Competing Frameworks

The MySQL vs PostgreSQL story isn't explained by ONE framework:

1. **Suite Integration** (user's thesis): Database choice is bundled with framework+platform
2. **Corporate Governance**: Oracle acquisition created trust issues, benefiting PostgreSQL and MariaDB
3. **Licensing Economics**: PostgreSQL BSD vs MySQL GPL matters for commercial software
4. **Talent Market**: Higher PostgreSQL salaries create hiring incentives
5. **Installed Base Inertia**: WordPress locks MySQL in place, migration costs too high
6. **Cultural Narratives**: "Boring technology" label is constructed, not objective
7. **Decision Fatigue**: Defaults reduce cognitive load, platforms provide those defaults
8. **Context-Dependent Trade-offs**: Neither is objectively better (see Uber counter-example)

**Key Insight:**
Database "wars" aren't won by better features. They're won by:
- Suite integration (LAMP, Heroku, Vercel)
- Switching costs that lock in old choices
- Licensing that enables/restricts use cases
- Talent market economics
- Cultural narratives ("boring" vs "innovative")
- Platform defaults that reduce decision burden

MySQL persists through inertia and real technical advantages for specific workloads.
PostgreSQL grows through new platform adoption and removing barriers (licensing, governance).

---

## USER'S KEY INSIGHTS (For Article)

### 1. "Boring Technology" is Rational, Not Conformist

**The Reframing:**
Friend argues: Choosing MySQL = conformity, obedience testing
User argues: Choosing MySQL = rational decision to save mental energy

**Why This Matters:**
- Dan McKinley's "Choose Boring Technology" isn't about being sheep
- It's about **finite cognitive resources** and **decision fatigue**
- Developers make hundreds of decisions per day
- Spending mental energy on databases means LESS energy for application logic
- **Database serves application development, not vice versa**

**The Distinction:**
- **Conformity**: Following others despite personal doubts, to fit in socially
- **Rational efficiency**: Following proven patterns to conserve cognitive resources for more valuable problems

Choosing LAMP stack with MySQL isn't "drinking the painful baijiu to prove loyalty" - it's "using the standard toolkit so I can focus on building my application."

### 2. Database Serves Application Development

**Core Principle:**
The database is infrastructure, not the product. Spending weeks evaluating MySQL vs PostgreSQL is time NOT spent building features customers want.

**Why Suite Integration Wins:**
- Reduces decision burden (pre-made choices)
- Reduces integration work (already tested together)
- Reduces debugging complexity (known patterns)
- Reduces cognitive load (documented workflows)

**The Inversion:**
Friend's narrative puts database choice at CENTER (requires courage, defines you as engineer).
Reality: Database choice should be at PERIPHERY (pick sensible default, move on).

### 3. PostgreSQL's Evolution Matters (Uber Case Revisited)

**What Happened:**
- Uber: PostgreSQL (9.1-9.2, 2011-2013) → MySQL (2016)
- Problems: Write amplification, replication lag, index bloat, upgrade difficulty

**The Nuance:**
- Uber used OLD PostgreSQL versions (9.1-9.2)
- By 2016, PostgreSQL had evolved significantly:
  - 9.4 (2014): JSONB, replication slots
  - 9.5 (2015): UPSERT, row-level security
  - 9.6 (2016): Parallel queries, better vacuuming

**Two Interpretations:**
1. **MySQL advocate**: "See, at scale PostgreSQL failed, MySQL better for write-heavy workloads"
2. **PostgreSQL advocate**: "Uber used outdated version and techniques, modern PostgreSQL fixes those issues"

**The Article Angle:**
Use Uber case to show database choice is TIME-DEPENDENT and WORKLOAD-DEPENDENT, not absolute. What's "better" depends on:
- Your specific workload (read vs write heavy)
- Your scale (small vs Uber-scale)
- Your team expertise
- The version you're using (2013 vs 2024)

---

## Reframing the Friend's Narrative

**Friend says:** MySQL dominance = cultural conformity (obedience test), PostgreSQL adoption = courage

**Better framing:**
1. **Suite theory**: Database choice is bundled, not standalone (LAMP, Heroku, Vercel)
2. **Rational efficiency**: "Boring technology" saves mental energy for real work
3. **Database serves application**: Infrastructure should fade into background
4. **Context matters**: No absolute "better" - depends on workload, scale, time period
5. **Switching costs**: MySQL persists through economics, not just inertia

**The key error in friend's narrative:**
Treats database choice as a MORAL decision (courage vs conformity) rather than a PRACTICAL decision (which suite, which defaults, which trade-offs).

The baijiu metaphor fails because:
- Baijiu tastes bad to everyone (objective physical reaction)
- Databases have different trade-offs for different contexts (subjective based on needs)
- Drinking baijiu serves social hierarchy (proves loyalty)
- Choosing database serves application development (enables product)

Totally different dynamics.

**What We Still Don't Know:**
- Why did SOME orgs choose PostgreSQL post-Oracle vs MariaDB?
- How does Chinese tech stack evolution differ from Western?
- What's the actual distribution of workload types (read-heavy vs write-heavy vs analytics)?
- Are bootcamps/education creating generational database preferences?
- When will migration costs drop enough for mass MySQL→PostgreSQL migration?

---

## Provocative Questions for the Article

1. **Is "better technology" even relevant?** If switching costs and suite integration dominate, does PostgreSQL's technical superiority matter?

2. **Should companies migrate?** If MySQL works and migration is risky/expensive, is staying on MySQL the rational choice even if PostgreSQL is "better"?

3. **Who benefits from the "PostgreSQL is winning" narrative?** Cloud vendors pushing managed PostgreSQL services? Consultants selling migration projects?

4. **Is this really about databases at all?** Or is it about framework evolution (PHP → Rails → Next.js) where database is just collateral damage?

5. **What's the Oracle conspiracy angle?** Did Oracle intentionally let MySQL stagnate to push enterprises toward Oracle DB, accidentally helping PostgreSQL?

6. **Is MySQL "dying" or just "stable"?** Mature technology doesn't grow fast. Is MySQL in maintenance mode or genuinely declining?

7. **What happens to the PostgreSQL DBAs when their salaries attract more people?** Will the 2x salary gap close as supply increases?

8. **Could a new database disrupt both?** Same way PostgreSQL disrupted MySQL by capturing new platforms, could DuckDB/something else disrupt PostgreSQL?

---

## Contradictions Worth Exploring

1. **PostgreSQL is "more mature" but also "more complex"** - How can it be both?

2. **PostgreSQL is "more popular" in surveys but MySQL has 6x larger deployment** - What does "winning" mean?

3. **Uber went MySQL→PostgreSQL→MySQL** - Does this prove anything or just prove it's complicated?

4. **"Choose boring technology" says MySQL, but PostgreSQL is 35 years old** - Who decides what's "boring"?

5. **PostgreSQL earns 2x salary but has fewer job postings** - Supply/demand or something else?

6. **Cloud vendors push PostgreSQL but AWS offers both** - Are they neutral or biased?

7. **More Stack Overflow questions for MySQL = bigger community OR more problems?** - Which interpretation is correct?

---

*These alternative perspectives complicate the simple narratives ("conformity" vs "suite thesis") and reveal a much messier reality where economics, psychology, inertia, and context all matter more than pure technical merit.*
