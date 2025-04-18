# Cloudless Web Application: Specification Document

---

### 🔍 Overview
The Cloudless Web Application is a user-friendly interface that allows users to submit computational tasks to the Cloudless distributed compute sharing system. It communicates with the existing Cloudless server to handle task submission, monitoring, and results retrieval.

---

### 📦 File Upload Architecture
**Direct Upload to Google Cloud Storage (GCS)**
The application uses a direct upload approach where files are uploaded directly to GCS without passing through the server. This provides better scalability, security, and performance.

1. **Server-Side (Existing Cloudless Server)**
   ```python
   # Endpoint to get signed URL for GCS
   @app.post("/api/upload-url")
   async def get_upload_url(filename: str, file_type: str):
       # Generate signed URL using StorageService
       return {
           "uploadUrl": signed_url,
           "filePath": gcs_path,
           "expiresAt": expiration_time
       }
   ```

2. **Client-Side (Web Interface)**
   ```html
   <!-- Simple HTML form with JavaScript for direct upload -->
   <form id="uploadForm">
     <input type="file" id="scriptFile" />
     <input type="file" id="dataFile" />
     <button type="submit">Upload</button>
   </form>

   <script>
   // Handle file upload
   async function uploadFile(file, type) {
     // 1. Get signed URL from server
     const response = await fetch('/api/upload-url', {
       method: 'POST',
       body: JSON.stringify({ filename: file.name, type: type })
     });
     const { uploadUrl, filePath } = await response.json();

     // 2. Upload directly to GCS
     await fetch(uploadUrl, {
       method: 'PUT',
       body: file
     });

     return filePath;
   }
   </script>
   ```

3. **Task Submission**
   ```python
   # Existing server endpoint
   @app.post("/api/tasks")
   async def submit_task(script_path: str, data_path: str, requirements: dict):
       # Use existing TaskService to handle the task
       return {"task_id": task_id, "status": "submitted"}
   ```

---

### ⚙️ Responsibilities

1. **User Interface**
   - Modern, responsive web interface
   - File upload interface for scripts and data
   - Task submission form with resource requirements
   - Real-time task monitoring dashboard
   - Results visualization and download

2. **File Management**
   - Drag-and-drop file upload interface
   - File type validation
   - Progress indicators for uploads
   - File preview capabilities
   - Secure file handling with GCS

3. **Task Management**
   - Task submission workflow
   - Resource requirement specification
   - Task status monitoring
   - Real-time progress updates
   - Error reporting and handling

4. **User Experience**
   - Intuitive navigation
   - Clear status indicators
   - Helpful error messages
   - Task history and management
   - Results organization

5. **Security**
   - User authentication
   - Secure file transfers
   - Session management
   - Access control

---

### 🚀 Frontend Architecture

```typescript
// Main components
interface Task {
    id: string;
    script: File;
    data: File;
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    result?: string;
}

// Key React components
<FileUploader>
    <ScriptUpload />
    <DataUpload />
</FileUploader>

<TaskForm>
    <ResourceSelector />
    <SubmitButton />
</TaskForm>

<TaskDashboard>
    <TaskList />
    <TaskDetails />
    <ProgressIndicator />
</TaskDashboard>

<ResultsViewer>
    <ResultPreview />
    <DownloadButton />
</ResultsViewer>
```

---

### 📁 File Structure

```
cloudless-user/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── templates/
│   ├── base.html
│   ├── upload.html
│   ├── dashboard.html
│   └── results.html
└── requirements.txt
```

---

### 📚 Key Features

1. **File Upload**
   - Simple file selection interface
   - Direct upload to GCS
   - Progress indicators
   - File type validation

2. **Task Management**
   - Task submission form
   - Real-time status updates
   - Error handling
   - Results download

3. **User Interface**
   - Clean, simple design
   - Responsive layout
   - Clear status indicators
   - Easy navigation

---

### 🔧 Technical Stack

Frontend:
- Simple HTML/CSS/JavaScript
- No complex frameworks needed
- Bootstrap or Tailwind CSS for styling
- Minimal JavaScript for file uploads and status updates

Communication:
- REST API with existing server
- WebSocket for real-time task updates
- Direct GCS upload using signed URLs

---

### 🌐 Authentication & Security
- JWT-based authentication
- Secure file uploads
- HTTPS everywhere
- CSRF protection
- Rate limiting

---

### 📝 Error Handling
- User-friendly error messages
- Retry mechanisms
- Fallback UI states
- Error logging
- Recovery procedures

---

### 🔄 Future Enhancements
- Advanced visualization tools
- Collaborative features
- Template system for common tasks
- Integration with ML platforms
- Mobile app version 