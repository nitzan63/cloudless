# CLOUDLESS ☁️❌

Cloudless is a decentralized distributed computing platform that enables users to both consume and contribute compute power. By connecting personal computers to a central system, anyone can run scalable distributed data processing jobs while others earn credits for sharing their idle resources.

---

## 🚀 Features

- Run distributed jobs at low cost using peer compute
- Upload scripts and data via a user-friendly UI
- Track job progress, logs, and download results
- Become a provider and earn credits
- Secure, scalable, and modular architecture

---

## 🏗️ Architecture Overview

Cloudless is made up of:

- **Frontend (React/Next.js)** – UI for consumers
- **Backend Microservices (Python)**:
  - Main Server – job orchestration
  - Task Executor – runs jobs via Spark (Livy)
  - Data Service – metadata and file storage
  - Register Service – handles provider VPN setup
  - Job Update Service – monitors job status
- **Workers (Docker/Spark)** – external nodes contributing compute
- **VPN Layer (WireGuard)** – secure communication between master and workers

---

## 🧱 Technologies Used

- Apache Spark
- Livy – REST interface for Spark
- RabbitMQ
- PostgreSQL
- WireGuard VPN
- Google Cloud Storage
- React, Next.js, TypeScript
- Python (Flask, FastAPI)

---

## 🔧 Setup

### Prerequisites

- Docker & Docker Compose
- WireGuard

---

## 👤 User Roles

### Consumers

- Submit processing tasks via web UI
- Monitor job logs and results

### Providers

- Run the worker container on your machine
- Join the VPN and contribute compute
- Earn credits based on usage

---

## 📄 Resources

- [📘 System Design Document (Google Drive)](https://docs.google.com/document/d/1AYFa5xPMDxbamOD0YjZ7Rpdrv-9eXOjWd2PZS60UbSs/edit?usp=sharing)
