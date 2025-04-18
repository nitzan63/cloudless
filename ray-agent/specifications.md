**Ray Agent: Specification Document**

---

### 🔍 Overview
The Ray Agent is a Dockerized background service that turns a user’s machine into a compute provider within a distributed task execution system. It connects to the central Ray cluster, registers with the management server, and waits to execute tasks. It is built to be cross-platform, headless, secure, and user-friendly.

---

### ⚙️ Responsibilities

1. **Cluster Connection**
   - Connect to Ray head node using `ray.init("ray://<head-ip>:<port>")`.
   - Ensure connection persists with retries on failure.

2. **Provider Registration**
   - On startup, call `POST /api/register` on the manager server.
   - Include system info: hostname, CPU cores, total memory, IP address.
   - Store registration token or provider ID for reuse.

3. **Heartbeat** *(Optional but Recommended)*
   - Send periodic `POST /api/heartbeat` to the manager with:
     - Provider ID
     - Current resource usage (CPU/mem)
     - Active Ray task count

4. **Docker Environment**
   - Run as a Docker container with minimal host dependencies.
   - Container must handle graceful shutdown (`SIGINT`, `SIGTERM`).

5. **Monitoring Loop**
   - Monitor Ray connection status.
   - Optionally tail Ray logs and post status to manager.

6. **Security**
   - Use HTTPS for manager API.
   - Use authentication tokens for register/heartbeat.
   - Only allow outbound connections (firewall friendly).

7. **Extensibility Hooks** *(future)*
   - UI for PyQt monitoring
   - Automatic updates
   - Idle shutdown

---

### 🚀 Launch Parameters

Environment Variables:
- `RAY_HEAD`: full address, e.g. `ray://34.134.59.39:10001`
- `MANAGER_URL`: e.g. `https://api.cloudless.ai/api/register`
- `CPU_LIMIT` (optional): container CPU reservation
- `MEMORY_LIMIT` (optional): memory reservation

---

### 📁 File Structure

```
ray-agent/
├── Dockerfile
├── main.py         # Entry point
├── register.py     # Handles API interaction
├── ray_utils.py    # Handles Ray init and monitoring
└── requirements.txt
```

---

### 📚 Future Ideas
- Task execution inside isolated Docker subcontainers
- GPU support detection
- Self-update from registry
- Integrate logs/metrics collection via Prometheus or OpenTelemetry

---

### 🌐 Expected Deployment
```bash
docker run -d \
  -e RAY_HEAD="ray://34.134.59.39:10001" \
  -e MANAGER_URL="https://your-api/api/register" \
  --cpus=2 \
  --memory=4g \
  yourdockerhubuser/ray-agent:latest
```

---

### 🔧 Minimum Requirements
- Python 3.11+
- Docker
- Internet access for outbound HTTPS

---

Let me know when you're ready to implement and I’ll help you build it step by step ✨

