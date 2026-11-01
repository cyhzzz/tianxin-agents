---
capability_id: audit-sop
title: 天信年报审计 SOP / 交付清单（整合卡）
one_liner: 把 11 张能力卡串成一条流水线——承接→风险评估→内控→程序→税务复核→编报→报告质控。天信年报审计的"总控台"。
intents:
  - 按 SOP 六步推进一份年报审计，不漏环节
  - 在每一步调用对应的能力卡
  - 产出标准化交付清单（底稿/报表/报告/质控表）
  - 把分散的能力卡组织成可执行的作业流程
keywords: [年报审计, SOP, 审计流程, 交付清单, 风险评估, 内控, 质控, 审计底稿, 审计报告, 天信作业]
importance: 极高（整合层，把所有卡串成可执行的县城所审计流水线）
---

## 一、核心理念

前面 11 张卡各自解决一个"点"（收入怎么确认、税怎么算、报表怎么编……）。但天信同事拿到一户年报，需要的是"按什么顺序做、每步调哪张卡、最后交什么"。本卡就是**总控台**——把点连成线，避免"会算税但不会串流程""审了程序忘了编报"。

## 二、判断直觉

**天信年报审计 SOP 六步**：

1. **承接与准则适用**（调 `small-business-standards.md`）：先定客户用小企业还是企业准则（排除法 + 三类排除），写进业务约定书/计划。
2. **风险评估与重要性**（调 `audit-core.md` R+M 段）：了解行业/业务/内控，列风险清单，算整体重要性 + 实际执行重要性。
3. **内控了解与测试**（调 `audit-core.md` + `reg-tips.md` 内控段）：评价内控设计有效性，决定依赖程度。
4. **进一步审计程序**（调 `audit-core.md` P 段 + 专项卡）：
   - 收入截止/总额净额 → `cas14-income.md`
   - 资产减值 → `asset-impairment-cas8.md`
   - 政府补助 → `government-grant-cas16.md`
   - 职工薪酬 → `employee-comp-cas9.md`
   - 函证/监盘/分析 → `audit-core.md` 四程序
5. **税务复核与纳税调整**（调 `tax-practice.md`）：所得税优惠适用、扣除限额、发票凭证合规。
6. **编报与报告质控**（调 `financial-statements-cas30.md` + `audit-core.md` 意见树 + `reg-tips.md` + `penalties.md`）：编平报表（过四勾稽）→ 形成意见 → 质控复核（回看处罚红线）。

**差错贯穿全程**：发现前期错 → `error-correction-cas28.md`。

## 三、准则依据

- 每步留痕：无底稿 = 没做（监管处罚高频源于"程序没做没留痕"，见 penalties 卡）。
- 重要性贯穿：错报汇总与重要性对比决定意见类型。
- 质控复核：合伙人终审，独立复核意见与红线。

# A2｜天信交付清单

| 交付物 | 内容 | 关联卡 |
|---|---|---|
| 审计计划 | 准则适用 + 风险清单 + 重要性 | small-business / audit-core |
| 程序底稿 | 函证/监盘/截止/分析 + 专项 | audit-core / cas14 / cas8 / cas16 / cas9 |
| 纳税调整表 | 优惠 + 限额 + 凭证合规 | tax-practice |
| 财务报表 | 四表/三表 + 附注（勾稽通过） | financial-statements-cas30 |
| 审计报告 | 意见类型 + 强调/说明段 | audit-core 意见树 |
| 质控复核表 | 红线核对（处罚/提示） | penalties / reg-tips |

## 五、演练输出

**输入**：一户中小制造企业年报审计任务（含基本资料）。
**输出**：
1. 给出六步推进计划（每步调哪张卡）；
2. 列出交付清单与责任人；
3. 标出高风险步骤（收入截止、存货监盘、纳税调整）；
4. 质控红线核对项。
**完成标准**：六步闭合、每步有卡可查、交付清单完整、红线已核对。

## 六、关联卡

本卡是总控，桥接到全部 11 张卡：
- `small-business-standards.md`（第1步）、`audit-core.md`（2/3/4/6步）、`cas14-income.md`（4步）、`asset-impairment-cas8.md`（4步）、`government-grant-cas16.md`（4步）、`employee-comp-cas9.md`（4步）、`tax-practice.md`（5步）、`financial-statements-cas30.md`（6步）、`error-correction-cas28.md`（贯穿）、`reg-tips.md` + `penalties.md`（6步质控）。

---
