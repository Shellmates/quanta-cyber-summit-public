# Deployment Guide for Infrastructure Team

## Quick Start

```bash
# Clone/extract the challenge files
cd virtual-escape

# Build and start the service
docker-compose up -d

# Check logs
docker-compose logs -f

# Test connection
nc localhost 9999
```


### Port Configuration

Change port in `docker-compose.yml`:

```yaml
ports:
  - "9999:9999"  # Change first number for external port
```

### Flag

Update `flag.txt` with the actual flag before building:

```bash
echo "flag{your_actual_flag_here}" > flag.txt
```

## Player Files Distribution

The `players_files/` folder contains files that should be distributed to participants. These typically include:
- Challenge description
- Starter code or tools
- Supporting files needed to solve the challenge

### Distribution Methods

**Option 1: Include in Challenge Package**
```bash
# Archive player files for distribution
zip -r virtual-escape-players.zip players_files/

# Or tar
tar -czf virtual-escape-players.tar.gz players_files/
```

### Files in players_files/

Players should receive:
- Challenge statement/README
- Any provided tools (e.g., `asm.py`)
- Sample exploit templates (if applicable)
- Any other starter files

**Do NOT distribute to players:**
- Flag file (`flag.txt`)
- Solution write-up (`solution/README.md`)
- Full source code (challenge binaries only via docker service)

## Resource Limits

Current limits (adjust in `docker-compose.yml`):

- Memory: 256MB
- CPU: 0.5 cores
- Max processes: 50
- Temp storage: 10MB

## Security Considerations

1. **Read-only filesystem**: Currently disabled for /tmp access. Consider if needed.
2. **User isolation**: Runs as non-root `ctf` user
3. **No privilege escalation**: `no-new-privileges:true` is set
4. **Resource limits**: Memory, CPU, and process limits applied

## Monitoring

### Health Check

```bash
# Check if service is running
docker-compose ps

# Test connection
echo "test" | nc localhost 9999

# View resource usage
docker stats
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use

```bash
# Find what's using the port
lsof -i :9999

# Or change the port in docker-compose.yml
```

### High resource usage

```bash
# Check container stats
docker stats

# Restart service
docker-compose restart

# Adjust limits in docker-compose.yml if needed
```

## Testing Checklist

Before going live:

- [ ] Service starts successfully
- [ ] Can connect via netcat
- [ ] Flag file is correct and readable by service
- [ ] Resource limits are appropriate
- [ ] Logs are being generated
- [ ] Test with exploit works
- [ ] Output is returned to client correctly

## Commands Reference

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Shell access (for debugging)
docker-compose exec vm_challenge /bin/bash

# Remove everything
docker-compose down -v --rmi all
```
