# SmartTeach AI

Smartteach Ai is an interactive educational assistant built using Streamlit. It helps students learn and test their knowledge through:

- AI-generated quizzes based on chosen topics  
- Chat functionality to ask questions and get answers from IBM WatsonX models  
- The ability to upload PDFs or images to provide additional context for better answers  
- A personal dashboard to track quiz scores and performance  
- A simple login and session system to keep your data organized  

This project is especially useful for learners who want a more interactive and intelligent way to study.

---

## Technologies and Tools Used

### App Interface
- **Streamlit** – Main framework used for building and deploying the web app  
- **streamlit-cookies-manager** – Helps manage user login sessions across page reloads  

### Authentication & File Management
- **hashlib** – Secures user passwords by hashing them  
- **json** – Handles user data and chat history  
- **os** – Manages file paths and directories  

### AI Model Integration
- **ibm-watsonx-ai** – Used to interact with IBM Foundation Models for quiz generation and chat responses  
- **Custom Python modules**:  
  - `utils/ibm_api.py` – Sends prompts to the IBM model and receives generated text  
  - `utils/model_selector.py` – Chooses the most suitable model based on prompt length  

### Extracting Text from Files
- **PyMuPDF (fitz)** – Extracts text from uploaded PDF files  
- **Pillow (PIL)** – Opens and processes image files  
- **pytesseract** – Performs OCR (Optical Character Recognition) to extract text from images  

### Other Libraries
- **beautifulsoup4** – For future web scraping needs  
- **soupsieve** – Helps filter and navigate HTML when using BeautifulSoup  

---

## Key Features

### User Functionalities
- Register and Login – Secure authentication with password protection  
- Quiz Generator – Choose a topic and difficulty, then receive a custom quiz  
- Ask Me – Ask the AI anything, with or without supporting documents  
- Dashboard – See your quiz performance and track progress  
- Resource Finder – Search and explore topics quickly  

### AI Capabilities
- Responses are powered by IBM WatsonX language models  
- Prompts are trimmed intelligently to fit model limits  
- Chat memory is maintained for each session  
- Uploaded PDFs or images can be used to provide context for better answers  

---

## How to Run This App Locally

### Prerequisites
- Python 3.10 or higher  
- pip installed  
- IBM WatsonX API and project id credentials  

### Setup Instructions

1. **Clone the repository:**
```sh 
git clone https://github.com/REGULA-DINESH/Smart-Teach-Ai.git
```
```sh 
cd smarthelp
```

2. **Create and activate Virtual Environment**
```sh 
conda create -p venv python==3.10
```
```sh 
conda activate venv/
```
</pre>
3. **Install required libraries::**
```sh 
pip install -r requirements.txt
```
4. **Add your secrets to .streamlit/secrets.toml**

Create a file .streamlit/secrets.toml and paste the following:

IBM_API_KEY = "your_ibm_api_key"
IBM_PROJECT_ID = "your_ibm_project_id"
IBM_URL = "https://your_ibm_project_url"

5. ** Run the Streamlit app: **
```sh 
streamlit run main.py
```
