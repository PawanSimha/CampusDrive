# Campus Drive 🎓

The ultimate platform for collaborative resource sharing among college students. Upload notes, question papers, and solutions, and access a vast library of study materials from your peers.

## 🚀 Features

### Core
-   **Secure Authentication**: Student and Teacher registration/login using `flask-login` and `bcrypt`.
-   **Dashboard**: Personalized dashboard to manage your activities.
-   **File Upload**: Securely upload PDF, DOCX, PPT, and images with UUID-based naming to prevent conflicts.

### Discovery & Interaction
-   **Advanced Browse**: Search by subject and filter by semester, branch, resource type, and privacy.
-   **Sorting**: Sort resources by **Latest**, **Highest Rated**, or **Most Popular**.
-   **Reviews & Ratings**: Rate resources (1-5 stars) and leave detailed reviews.
-   **Download Tracking**: Monitor the popularity of resources with download counters.
-   **Subject Folders**: Navigate resources easily via subject-specific folders.

### Administration & Security
-   **Admin Panel**: Dedicated dashboard for admins to manage users and delete inappropriate contents.
-   **Access Control**: strictly enforced precision-based access control; private resources are only visible to students from the uploader's college.

## 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd Campus DriveApp
    ```

2.  **Install Dependencies**
    It's recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    pip install certifi  # Recommended for Windows/SSL issues
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```env
    MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/webcrawlers_db?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true
    SECRET_KEY=YourSecretKeyHere
    ```
    *Note: Ensure your IP address is whitelisted in MongoDB Atlas Network Access (0.0.0.0/0 for testing).*

4.  **Run the Application**
    ```bash
    python app.py
    ```
     Access the app at `http://127.0.0.1:5000`.

## 👨‍💻 Usage

-   **Register**: Create a new account. Select "Student" or "Teacher".
-   **Upload**: Share your study materials. set privacy to 'Private' to restrict access to your college peers only.
-   **Admin Access**: To access the admin panel at `/admin`, you need a user with `role="admin"`. You can register a user and select the Admin role (for demo purposes) or update the role manually in the database.

## 📂 Project Structure

-   `app.py`: Main application logic and routes.
-   `templates/`: HTML templates (Bootstrap 5).
-   `static/uploads/`: Stored resource files.
-   `config.py`: Configuration settings.

## 🤝 Contribution

Feel free to fork this project and submit pull requests. For major changes, please open an issue first.

---
**Built for Ramaiah Hackathon**
