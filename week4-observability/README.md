# Week 4: Observability with Prometheus & Grafana

## Objectives:  
✅ Instrument FastAPI app with Prometheus metrics  
✅ Deploy Prometheus to Kubernetes  
✅ Deploy Grafana to Kubernetes  
✅ Create custom dashboards  
✅ Set up alerting rules  
✅ Monitor your wallet service in real-time  

## Architecture:

**Before (Week 3):**
```
Ingress → Wallet Service (2 pods) → DynamoDB
```

**After (Week 4):**
```
Ingress → Wallet Service (2 pods, instrumented) → DynamoDB
              ↓ (metrics)
          Prometheus (scrapes metrics)
              ↓ (queries)
          Grafana (visualization)
              ↓
          Me! (dashboards + alerts)
```

---




