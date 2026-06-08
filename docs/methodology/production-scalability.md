# Production Scalability & Deployment Path

## From Research to Production

The FHIRBench agentic architecture is designed to map directly from a local research setup to production-grade clinical AI infrastructure. This section documents the deployment path, demonstrating that the benchmark methodology is not merely academic but serves as validation for production middleware.

## Architecture Mapping: Local → Cloud

| Research (Local) | Production (AWS) | Function |
|-----------------|------------------|----------|
| Quick Desktop | AWS AgentCore | Agent orchestration |
| Zotero MCP (local process) | AgentCore Tool (hosted MCP) | Bibliography / knowledge management |
| GitHub MCP (local process) | AgentCore Tool (hosted MCP) | Version control + CI/CD |
| Kiro (ACP coding agent) | AgentCore Agent (managed) | Code generation + execution |
| Amazon Bedrock (cloud) | Amazon Bedrock (same) | Model inference |
| Local Python venv | ECS/Fargate containers | Serialization pipeline runtime |

## Why This Matters

The benchmark framework (FHIRBench) validates the core hypothesis: **serialization strategy significantly impacts LLM accuracy on clinical tasks**. The architecture simultaneously proves that:

1. **The methodology is reproducible** — single AWS account replicates all results
2. **The pipeline is production-ready** — MCP servers can be deployed as managed services
3. **The scaling path is defined** — local → EC2 → AgentCore with zero code changes

## Production Deployment Options

### Option A: EC2 (Team-Scale)
```
EC2 Instance (t3.medium, ~$30/mo)
├── Zotero MCP server (always-on)
├── GitHub MCP server (always-on)
├── Serialization API (FastAPI)
└── Bedrock client (boto3)
```
- **Best for:** Small team (2-5 researchers) sharing infrastructure
- **Cost:** ~$30-50/month + Bedrock usage

### Option B: AWS AgentCore (Enterprise-Scale)
```
AgentCore (managed)
├── Registered Tools (MCP servers)
│   ├── FHIR Serializer Tool
│   ├── Clinical Evaluator Tool
│   └── Reference Manager Tool
├── Registered Agents
│   ├── Data Pipeline Agent
│   ├── Benchmark Agent
│   └── Analysis Agent
└── Bedrock Integration (native)
```
- **Best for:** Enterprise clinical AI teams, multi-tenant, auto-scaling
- **Cost:** Pay-per-invocation, zero idle cost

### Option C: Serverless (Cost-Optimized)
```
Lambda Functions
├── serialize_fhir() — stateless serialization
├── evaluate_response() — scoring
├── generate_report() — analysis
└── API Gateway (REST endpoints)
```
- **Best for:** Sporadic usage, CI/CD pipeline integration
- **Cost:** Near-zero when idle, ~$0.001 per evaluation

## Paper Positioning

This scalability dimension strengthens the paper's contribution in two ways:

1. **Section 5 (Discussion):** "The FHIRBench framework is designed for direct deployment as production middleware, validating both the academic contribution and practical utility."

2. **Section 6 (Future Work):** "The local agentic architecture demonstrated here maps to production deployment via AWS AgentCore, enabling enterprise clinical AI teams to adopt optimized serialization strategies as managed services without reimplementation."

## Key Insight

> The benchmark IS the product prototype. Building FHIRBench for the paper = building the serialization middleware. The paper validates the approach, the code becomes the product, and the architecture proves production viability. Triple duty.
