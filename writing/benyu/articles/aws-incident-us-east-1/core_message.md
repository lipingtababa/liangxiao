# Core Message: AWS as Internet Single Point of Failure

## Core Thesis

云计算承诺了分布式和高可用，但AWS（特别是US-EAST-1）已成为互联网的单点故障。这是一个无法通过技术手段解决的systemic risk，需要监管介入。

---

## Logical Argument Structure

### 论点1：AWS已成为互联网基础设施的必需依赖
*(Foundation - establishes the problem exists)*

**核心主张：**
- 直接依赖：95个AWS服务在一次故障中同时受影响
- 间接依赖：六级依赖链（汽车贷款 → Kreditz → Yapily → 英国银行 → AWS服务 → US-EAST-1）
- 全局依赖：Global services（IAM, DynamoDB Global Tables）依赖单一region

**Evidence needed:**
- ✅ Six-level dependency chain (Kreditz → Yapily → UK Banks → AWS US-EAST-1)
- ⏳ What % of internet services depend on AWS?
- ⏳ Examples of non-AWS companies affected through indirect dependencies

**For regulators:** This is like power grid dependency - you may not buy electricity from one company, but your supplier's supplier does.

---

### 论点2：迁移成本制造了lock-in效应
*(Why the problem persists - explains why market can't self-correct)*

**核心主张：**
- GitHub, LinkedIn talked about AWS migration for years
- Even knowing the SPOF risk, companies can't leave
- This isn't free market choice - it's structural lock-in

**Evidence needed:**
- ⏳ GitHub/LinkedIn migration timeline (when did they start talking? Did they finish?)
- ⏳ What makes migration prohibitively expensive?
  - Re-architecture cost?
  - Proprietary APIs (Lambda, DynamoDB)?
  - Training/hiring cost?
- ⏳ Multi-cloud doesn't solve this (Global services still depend on US-EAST-1)

**For regulators:** This is vendor lock-in at infrastructure level. Market competition isn't working because switching costs are too high.

---

### 论点3：AWS自身的复杂度已超出其工程能力
*(Why AWS can't fix it themselves - the technical impossibility)*

**核心主张：**
- AWS工程师花了8.5小时才找到root cause
- 三次改口：DNS → EC2网络 → NLB健康检查
- 需要手动限流、手动throttling（说明缺乏自动熔断机制）
- 恢复耗时13小时，串行恢复每一层依赖

**Evidence needed:**
- ✅ Timeline of AWS's changing explanations (from status.md)
- ✅ Manual interventions required (throttling, SQS polling reduction)
- ⏳ How many times has US-EAST-1 caused outages? (Historical pattern)
- ⏳ Is AWS complexity growing faster than their ability to manage it?

**For regulators:** Even the operator can't control their own system. This is like a nuclear plant where engineers don't fully understand the reactor.

---

### 论点4：信息不对称使客户无法评估风险
*(Why customers can't protect themselves - the transparency problem)*

**核心主张：**
- 95个服务受影响，AWS只公布17个
- Kreditz不知道自己六级依赖于US-EAST-1
- 没有公开的dependency graph
- 客户无法做informed decision或设计灾备策略

**Evidence needed:**
- ✅ 95 services affected, only 17 disclosed
- ✅ Kreditz's discovery process (didn't know about six-level chain until it broke)
- ⏳ Does AWS provide any dependency documentation?
- ⏳ Other companies' similar experiences

**For regulators:** This is information asymmetry. AWS knows the dependencies, customers don't. Can't make risk-informed decisions.

---

## The Logical Chain

```
论点1: Everyone depends on AWS (directly or indirectly)
   ↓
论点2: Can't migrate out (lock-in effect)
   ↓
论点3: AWS can't manage its own complexity
   ↓
论点4: Customers can't assess risk (no transparency)
   ↓
结论: Systemic risk that market can't solve
   ↓
需要监管介入
```

**The logic:**
- **IF** everyone depends on AWS (论点1)
- **AND** they can't leave (论点2)
- **AND** AWS can't manage it (论点3)
- **AND** customers can't protect themselves (论点4)
- **THEN** this is a market failure requiring regulatory intervention

---

## Target Audience

**Primary:**
- Technical people (understand dependency chains, distributed systems)
- Regulators (China, EU - care about systemic risk and sovereignty)

**Goal:**
- Trigger discussion in China and EU about cloud infrastructure regulation
- Raise awareness of indirect dependencies

---

## Geographic/Regulatory Framing

### For China:

**Sovereignty angle:**
- Chinese companies depend on US infrastructure (US-EAST-1)
- US government could theoretically weaponize this dependency
- 六级依赖意味着：即使你不直接用AWS，你的供应商的供应商可能在用

**Regulatory precedent:**
- China regulates telecoms, banks, power grids
- Cloud infrastructure is now equally critical
- Should require: dependency disclosure, data sovereignty, migration paths

### For EU:

**GDPR/Digital sovereignty angle:**
- EU companies depend on US-EAST-1 for global services
- GDPR requires data protection, but what about availability protection?
- Digital Markets Act (DMA) targets gatekeepers - is AWS a gatekeeper?

**Regulatory precedent:**
- EU regulates critical infrastructure (NIS2 Directive)
- Cloud providers should be subject to similar requirements
- Require: transparency, interoperability, portability

---

## Key Evidence

### What We Have:

1. **Six-level dependency chain:**
   ```
   汽车贷款公司 → Kreditz → Yapily → UK Banks → AWS third-party service → AWS US-EAST-1
   ```
   - Kreditz couldn't provide credit scores for loans
   - Discovered post-mortem
   - Level 5 still being investigated

2. **AWS incident timeline:**
   - 95 services affected, only 17 explicitly mentioned
   - 8.5 hours to identify root cause (12:11 AM → 8:43 AM PDT)
   - Three different root cause explanations
   - 13 hours total duration
   - Manual interventions required (throttling, rate limiting)

3. **Recovery complexity:**
   - Serial recovery (each level waits for previous)
   - Manual adjustments to SQS polling rates
   - Manual EC2 launch throttling
   - Backlog processing took hours after "recovery"

### What We Need:

**Critical:**
1. Timeline of Kreditz recovery (when could users actually get credit scores?)
2. GitHub/LinkedIn migration stories (verification)
3. AWS dependency documentation status (does any exist?)

**Strong support:**
4. AWS US-EAST-1 historical outage frequency
5. Market share data (AWS overall, US-EAST-1 specifically)
6. Other companies' multi-level dependency stories

**Nice to have:**
7. Which UK banks were affected (to identify Level 5 service)
8. GCP/Azure comparison (similar centralization issues?)
9. Migration cost estimates

---

## Anticipated Counterarguments

### "Not everyone depends on AWS" (vs 论点1)
**Response:** Direct (32% market share) + Indirect (six-level chains). Even non-AWS companies depend on services that use AWS.

### "Migration is a business choice" (vs 论点2)
**Response:** Switching cost ≠ choice. Multi-cloud doesn't solve US-EAST-1 dependency for global services.

### "8.5 hours is reasonable for complex systems" (vs 论点3)
**Response:** Three false starts show they don't understand their own system. Lack of auto-circuit breakers = architecture problem.

### "AWS provides SLAs" (vs 论点4)
**Response:** SLAs describe outcomes, not risks. Can't make informed decisions without dependency graphs.

### "Market will solve this" (vs 结论)
**Response:** 论点2 proves customers can't leave. Critical infrastructure requires regulation (power grids, telecoms).

---

## Possible Calls-to-Action

**For companies:**
- Demand dependency transparency from vendors
- Document your own dependency chains
- Pressure AWS for better documentation

**For regulators:**
- Classify cloud as critical infrastructure
- Require dependency disclosure (like ingredient labels)
- Mandate interoperability standards

**For AWS:**
- Publish service dependency graphs
- Commit to decentralizing global services
- Provide migration tooling
