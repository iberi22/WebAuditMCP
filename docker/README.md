# Docker Deployment Guide

## 🚀 Quick Start

### 1. Build and Start the Container

```bash
# Navigate to project root
cd e:\scripts-python\webscanMCP

# Build and start the MCP Auditor
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f auditor
```

### 2. Verify Server is Running

```bash
# Check container status
docker ps | findstr mcp-auditor

# Test the health endpoint
curl http://localhost:8000/mcp
```

### 3. Connect from Client

**Using FastMCP Client:**
```python
from fastmcp import Client
import asyncio

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        result = await client.call_tool("health_check", {})
        print(f"Health: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Using VS Code:**
Configure `.vscode/mcp.json`:
```json
{
  "servers": {
    "auditor-docker": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## 📦 Container Management

### Start/Stop/Restart

```bash
# Start
docker-compose -f docker/docker-compose.yml up -d

# Stop
docker-compose -f docker/docker-compose.yml stop

# Restart
docker-compose -f docker/docker-compose.yml restart

# Stop and remove
docker-compose -f docker/docker-compose.yml down
```

### View Logs

```bash
# All logs
docker-compose -f docker/docker-compose.yml logs

# Follow logs in real-time
docker-compose -f docker/docker-compose.yml logs -f

# Specific service
docker logs mcp-auditor -f
```

### Rebuild Image

```bash
# Rebuild and restart
docker-compose -f docker/docker-compose.yml up -d --build

# Force rebuild without cache
docker-compose -f docker/docker-compose.yml build --no-cache
```

## 🔧 Advanced Configuration

### Enable OWASP ZAP (Optional)

```bash
# Start with ZAP profile
docker-compose -f docker/docker-compose.yml --profile zap-scan up -d

# ZAP will be available at http://localhost:8080
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example
cp .env.example .env

# Edit with your values
WAVE_API_KEY=your_api_key_here
CHROME_MCP_ENABLED=true
```

### Custom Port

Edit `docker/docker-compose.yml`:

```yaml
ports:
  - "9000:8000"  # Map to port 9000 instead
```

### Resource Limits

Edit `docker/docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Increase CPU limit
      memory: 4G       # Increase memory limit
```

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs mcp-auditor

# Check resource usage
docker stats mcp-auditor

# Verify port is available
netstat -ano | findstr :8000
```

### Health Check Failing

```bash
# Check health status
docker inspect mcp-auditor | findstr Health

# Test endpoint manually
docker exec mcp-auditor curl -f http://localhost:8000/mcp
```

### Permission Issues

```bash
# Check artifacts directory permissions
ls -la artifacts/

# Fix permissions (Linux/Mac)
chmod -R 755 artifacts/
```

## 🧹 Cleanup

### Remove Everything

```bash
# Stop and remove containers
docker-compose -f docker/docker-compose.yml down

# Remove images
docker rmi mcp-auditor:latest

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a
```

## 📊 Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker/docker-compose.yml mcp-auditor

# Check services
docker service ls

# Scale service
docker service scale mcp-auditor_auditor=3
```

### Using Kubernetes

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-auditor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-auditor
  template:
    metadata:
      labels:
        app: mcp-auditor
    spec:
      containers:
      - name: auditor
        image: mcp-auditor:latest
        ports:
        - containerPort: 8000
        env:
        - name: CHROME_MCP_ENABLED
          value: "true"
```

## 📈 Monitoring

### Health Checks

```bash
# Watch health status
watch 'docker inspect mcp-auditor | grep -A 5 Health'

# Prometheus metrics (if enabled)
curl http://localhost:8000/metrics
```

### Resource Usage

```bash
# Real-time stats
docker stats mcp-auditor

# Historical usage
docker history mcp-auditor:latest
```

## 🔐 Security Best Practices

1. **Don't expose port 8000 publicly** - Use a reverse proxy (nginx, Traefik)
2. **Add authentication** - Enable Bearer token or OAuth
3. **Use secrets** - Store sensitive data in Docker secrets or environment variables
4. **Regular updates** - Rebuild images with latest security patches
5. **Network isolation** - Use Docker networks to isolate services

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
