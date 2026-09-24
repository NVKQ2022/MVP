# Implementation Plan: Face Authentication Integration

## 1. Overview & Objective
Implement the end-to-end Face Authentication feature following the flow specified in `FLOW.md`:
1. **Frontend:** Detect face using MediaPipe BlazeFace, crop the face frame on the client, and send `multipart/form-data` to the backend.
2. **Backend (.NET):** Receive the cropped face file in `AuthController`, delegate to `FaceAuthenticateService` to extract the 512-D embedding via the Python AI microservice, query Qdrant vector database for identity match, and return JWT tokens.
3. **Safety Constraint:** Strictly isolate changes to the face authentication components. Do not touch or modify any unrelated features or pages.

---

## 2. Step-by-Step Implementation Plan

### Phase 1: Frontend Implementation

#### Step 1.1: Expose Face Cropping in `FaceDetection.jsx`
* **Target File:** [`Front-end/src/features/auth/components/FaceRecognition/FaceDetection.jsx`](file:///home/quan/projects/maivenpoint/MidTerm/university-portal-BE-feature-ai-authenticate/Front-end/src/features/auth/components/FaceRecognition/FaceDetection.jsx)
* **Actions:**
  - Wrap `FaceDetection` with React `forwardRef`.
  - Maintain a ref `latestDetectionRef` updated inside `predictLoop` storing the most recent detected face bounding box `(originX, originY, width, height)` and mirrored state.
  - Use `useImperativeHandle` to expose a `captureCroppedFace(): Promise<Blob>` method:
    - Verifies video is playing and a face is detected.
    - Adds a ~15% bounding box margin for canonical facial coverage.
    - Draws the sliced video frame onto an offscreen `<canvas>`.
    - Returns a JPEG `Blob` via `canvas.toBlob(resolve, 'image/jpeg', 0.95)`.
* **Verification:** Test ref invocation from parent component; ensure exported Blob is valid JPEG image data.

#### Step 1.2: Add Face Login API Method
* **Target File:** [`Front-end/src/features/auth/services/auth.api.js`](file:///home/quan/projects/maivenpoint/MidTerm/university-portal-BE-feature-ai-authenticate/Front-end/src/features/auth/services/auth.api.js)
* **Actions:**
  - Add `faceLogin(formData)` calling `POST /api/v1/Auth/face-login`.
  - Set request header `'Content-Type': 'multipart/form-data'`.
  - Clean up the existing duplicate `register` property in the `authApi` object.
* **Verification:** Method returns parsed `res.data` containing `accessToken`, `expiresAt`, `refreshToken`.

#### Step 1.3: Update `useAuth.js` Hook
* **Target File:** [`Front-end/src/features/auth/hooks/useAuth.js`](file:///home/quan/projects/maivenpoint/MidTerm/university-portal-BE-feature-ai-authenticate/Front-end/src/features/auth/hooks/useAuth.js)
* **Actions:**
  - Add `faceLogin(formData)` action:
    - Calls `authApi.faceLogin(formData)`.
    - Decodes JWT access token using `jwtDecode`.
    - Updates `authStore` with user profile and tokens.
    - Returns the auth payload for redirection.
* **Verification:** Ensure `authStore.getSnapshot()` reflects authenticated status with valid tokens.

#### Step 1.4: Wire Up Face Login in `LoginForm.jsx`
* **Target File:** [`Front-end/src/features/auth/components/LoginForm/LoginForm.jsx`](file:///home/quan/projects/maivenpoint/MidTerm/university-portal-BE-feature-ai-authenticate/Front-end/src/features/auth/components/LoginForm/LoginForm.jsx)
* **Actions:**
  - Attach `faceDetectionRef` to `<FaceDetection ref={faceDetectionRef} />`.
  - Update `handleFaceLogin`:
    - Ensure `liveFaceCount === 1` before allowing capture.
    - Call `faceDetectionRef.current.captureCroppedFace()`.
    - Construct `FormData`:
      - `formData.append('Capture', blob, 'face_capture.jpg')`
      - `formData.append('DeviceId', navigator.userAgent)`
    - Invoke `faceLogin(formData)`.
    - On success: close dialog and navigate to `/` (or admin host if user is Admin).
    - On error: display user-friendly error message (`"Face not recognized. Please try again or use your password."`).
* **Verification:** User clicking "Verify Face" triggers camera capture, loading indicator displays during network request, and error/success states render correctly.

---

### Phase 2: Backend Implementation (.NET 10 API)

#### Step 2.1: Add `FaceRecognition` Options to `appsettings.json`
* **Target File:** [`Back-end/FirstAPIProject/FirstAPIProject/appsettings.json`](file:///home/quan/projects/maivenpoint/MidTerm/university-portal-BE-feature-ai-authenticate/Back-end/FirstAPIProject/FirstAPIProject/appsettings.json)
* **Actions:**
  - Add the `"FaceRecognition"` configuration section:
    ```json
    "FaceRecognition": {
      "BaseUrl": "http://localhost:8000",
      "ExtractEmbeddingEndpoint": "/api/v1/embedding/file"
    }
    ```
* **Verification:** Backend configuration binder populates `FaceRecognitionOptions` with non-empty `BaseUrl` and correct endpoint.

#### Step 2.2: Expose `[HttpPost("face-login")]` in `AuthController.cs`
* **Target File:** [`Back-end/FirstAPIProject/FirstAPIProject/Controllers/AuthController.cs`](file:///home/quan/projects/maivenpoint/MidTerm/university-portal-BE-feature-ai-authenticate/Back-end/FirstAPIProject/FirstAPIProject/Controllers/AuthController.cs)
* **Actions:**
  - Inject `IFaceAuthenticateService _faceAuthenticateService` into `AuthController` constructor.
  - Implement endpoint:
    ```csharp
    [HttpPost("face-login")]
    [Consumes("multipart/form-data")]
    public async Task<IActionResult> FaceLogin(
        [FromForm] FaceAuthenticateLoginRequest request,
        CancellationToken cancellationToken)
    {
        var response = await _faceAuthenticateService.FaceAuthenticateAsync(request, cancellationToken);
        return Ok(response);
    }
    ```
* **Verification:** Endpoint appears in Swagger / OpenAPI documentation and responds to `multipart/form-data` requests.

#### Step 2.3: Calibrate Vector Search Threshold
* **Target File:** [`Back-end/FirstAPIProject/FirstAPIProject.Infrastructure/VectorDb/Repositories/FaceEmbeddingRepository.cs`](file:///home/quan/projects/maivenpoint/MidTerm/university-portal-BE-feature-ai-authenticate/Back-end/FirstAPIProject/FirstAPIProject.Infrastructure/VectorDb/Repositories/FaceEmbeddingRepository.cs)
* **Actions:**
  - Adjust `threshold` from `0.8f` to `0.45f - 0.50f` to align with ArcFace cosine similarity characteristics.
* **Verification:** Test vector search matching with real ArcFace embeddings to ensure genuine matches score above threshold while imposter faces score below.

---

### Phase 3: AI Microservice Verification & Integration Testing

#### Step 3.1: Python FastAPI Service Verification
* **Target Directory:** [`AI/FaceAuthentication/Recognition`](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition)
* **Actions:**
  - Verify FastAPI endpoint `/api/v1/embedding/file` is accessible and accepts `UploadFile` (multipart form field `file`).
  - Confirm returned JSON structure: `{ "success": true, "embedding": [...] }`.
* **Verification:** Run a test curl / HTTP POST sending an image file to `http://localhost:8000/api/v1/embedding/file`.

#### Step 3.2: End-to-End Test Execution
* **Testing Flow:**
  1. Open Frontend at `http://localhost:5173`.
  2. Click "Face login" to open dialog.
  3. Allow webcam permissions; verify live bounding box and landmark tracking.
  4. Click "Verify Face"; confirm frontend captures face slice and sends `FormData`.
  5. Confirm .NET receives file, posts to FastAPI `/api/v1/embedding/file`, and receives 512-D float vector.
  6. Confirm Qdrant matches the user and returns `AuthResponse`.
  7. Confirm Frontend stores session and navigates to the authenticated dashboard.

---

## 3. Rollback & Isolation Strategy
- All modifications are strictly restricted to:
  - `Front-end/src/features/auth/`
  - `Back-end/FirstAPIProject/.../Controllers/AuthController.cs`
  - `Back-end/FirstAPIProject/.../Repositories/FaceEmbeddingRepository.cs`
  - `Back-end/FirstAPIProject/.../appsettings.json`
- No shared UI primitives, routes, admin components, or student features outside of auth are modified.
