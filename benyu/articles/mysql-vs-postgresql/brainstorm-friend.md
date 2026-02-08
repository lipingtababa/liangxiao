# Brainstorm Material - From Friend

## Core Metaphor: MySQL as "Obedience Test" (服从测试)

### Main Argument
MySQL's dominance in Chinese internet industry is like 白酒 (baijiu) culture at business dinners - a form of institutional conditioning/obedience testing rather than technical merit.

### Key Points

#### 1. Two Unpleasant Drinks (两杯难喝的酒)
- First time drinking baijiu: body rejects it (tastes terrible)
- First time seriously examining MySQL: brain rejects it (design flaws)
- Both: "you'll get used to it" (习惯就好了)

MySQL design issues cited:
- Default charset latin1, not UTF-8; utf8 is fake, real one is utf8mb4
- TIMESTAMP only to 2038 (Y2K ghost)
- Transaction ACID has serious problems
- GROUP BY can select non-aggregate columns (violates SQL standard)
- No real BOOLEAN type (just TINYINT(1) alias)
- DDL doesn't support transactions
- Replication lag, optimizer issues

#### 2. Formation of Discipline (规训的形成)
- Baijiu culture spread top-down: from specific organizations → bureaucracy → whole society
- MySQL spread same way: Silicon Valley/big tech → BAT → entire Chinese internet
- Not because it's best, but because "authorities use it"
- People follow without comparing alternatives

#### 3. Obedience Test (服从测试)
- Baijiu tests: will you endure discomfort for this relationship?
- MySQL tests: will you conform to industry norms?

Choosing MySQL = safe, no explanation needed
Choosing PostgreSQL = requires courage, justification, risk

#### 4. Personal Story (亲历者故事)
Author's experience at Alibaba:
- Had to fight hard to use PostgreSQL + Go
- Got pushed out of project
- Replacement immediately switched back to Java + MySQL
- Not due to technical problems, just to return to "safe zone"
- Author left Alibaba for companies using PostgreSQL/Go (Tantan, Apple)

#### 5. Truth Serum (吐真剂)
Database choice reveals engineer's thinking:
- "MySQL is enough" → never experienced better
- "Everyone uses MySQL" → follows crowd
- "PostgreSQL learning curve too steep" → spent 3 years learning MySQL workarounds, won't spend 3 months on better system
- "Team doesn't know it" → team's technical investment is wrong
- "Migration risk too high" → already locked into MySQL

#### 6. Tide is Turning (潮水的方向)
Evidence PostgreSQL is winning:
- Cloud providers (AWS, Google, Azure) push PostgreSQL
- AI era: pgvector makes PostgreSQL vector DB of choice
- Licensing: PostgreSQL pure BSD vs MySQL GPL (Oracle)
- GitHub: new projects choose PostgreSQL
- DB-Engines, StackOverflow, JetBrains surveys show PostgreSQL fastest growing

#### 7. Courage to Choose (选择的勇气)
- MySQL works, but "appropriate choice" ≠ "default choice"
- Former is result of thinking, latter is product of conditioning
- PostgreSQL needs courage in China - courage to break inertia, think independently
- Same courage as saying "I don't drink baijiu" at business dinner

### Related Articles Listed
Multiple articles about PostgreSQL vs MySQL debates, performance comparisons, industry trends

---

## User's Counter-Argument

"I don't think his argument stands. I think mysql won because it has a development suite called LAMP, which postgresql doesn't"

- LAMP stack (Linux, Apache, MySQL, PHP) as integrated development suite
- PostgreSQL lacked this kind of packaged ecosystem/marketing
- Technical bundling advantage, not just social conformity
