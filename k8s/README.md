# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Distributed Chess Engine Evaluation Platform.

## Prerequisites

- Kubernetes cluster (minikube, GKE, EKS, or local cluster)
- kubectl configured
- Docker images built and pushed to a registry (or use local images with minikube)

## Deployment Steps

1. **Create namespace:**
   ```bash
   kubectl apply -f namespace.yaml
   ```

2. **Deploy Redis:**
   ```bash
   kubectl apply -f redis-deployment.yaml
   ```

3. **Build and push Docker images:**
   ```bash
   # Build images
   docker build -f docker/Dockerfile.api -t chess-evaluation-api:latest .
   docker build -f docker/Dockerfile.worker -t chess-evaluation-worker:latest .
   
   # For minikube, load images directly:
   minikube image load chess-evaluation-api:latest
   minikube image load chess-evaluation-worker:latest
   
   # Or push to registry:
   docker tag chess-evaluation-api:latest your-registry/chess-evaluation-api:latest
   docker push your-registry/chess-evaluation-api:latest
   ```

4. **Deploy API and Workers:**
   ```bash
   kubectl apply -f api-deployment.yaml
   kubectl apply -f worker-deployment.yaml
   ```

5. **Check status:**
   ```bash
   kubectl get pods -n chess-evaluation
   kubectl get services -n chess-evaluation
   ```

6. **Access the API:**
   ```bash
   # Port forward to access locally
   kubectl port-forward -n chess-evaluation service/chess-api 8000:80
   ```

## Scaling

Scale workers horizontally:
```bash
kubectl scale deployment chess-worker --replicas=5 -n chess-evaluation
```

## Monitoring

Access Prometheus metrics:
```bash
kubectl port-forward -n chess-evaluation deployment/chess-api 9090:9090
curl http://localhost:9090/metrics
```

