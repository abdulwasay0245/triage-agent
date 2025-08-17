from fastapi import FastAPI
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel 
from agents.run import RunConfig
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from agents import enable_verbose_stdout_logging

# enable_verbose_stdout_logging()
app = FastAPI()

load_dotenv()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"
                   ,"https://resumecraft-pearl.vercel.app"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)


config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
education_summary_agent = Agent(
    name=" Summary Agent",
    instructions="You are an expert content writer,and be recieving some education details , eg: Work experience like where did the jobs and job roles,skills, education year , university or institute name degree or field name make a good summary and professional summary of it of max 4 lines.Especially dont include any heading or any other thing like here is your summary just only give me only 1 summary ",
    model=model,
)
job_summary_agent = Agent(
    name="Job Summary Agent",
    instructions='''
    You are an expert content writer.  
You will be given structured job details (work experience, job roles, skills, education, years, university/institute, degree/field).  

Generate a concise professional summary (maximum 4 lines).  

The output must follow these rules strictly:  
- Return **only valid JSON** (no markdown formatting, no triple backticks, no "json" labels).  
- Create a top-level key `"job_summary"`.  
- `"job_summary"` must be an array of exactly **3 bullet points**.  
- Each bullet point should describe what the person did in this role or what they learned.  
- Do not include any text outside the JSON object.  

Example output:
{
  "job_summary": [
    "Led software development projects, collaborating with cross-functional teams to deliver scalable solutions.",
    "Enhanced expertise in Python, FastAPI, and REST APIs while ensuring code quality and performance.",
    "Applied problem-solving and communication skills to improve project efficiency and client satisfaction."
  ]
}
''',
    model=model,
)


# triage_agent = Agent(
#     name="Triage Agent",
#     instructions="""
# You are an expert project manager. 
# You will receive combined information that includes both job experience and educational background.

# Step 1: Extract the education-related part of the input and send it to the education_summary_agent.
# Step 2: Extract the job-related part of the input and send it to the job_summary_agent.
# Step 3: Collect both summaries and return them in a single JSON with two keys: 
#     - "education_summary": (value from education_summary_agent)
#     - "job_summary": (value from job_summary_agent)

# Do NOT add any other commentary. Return only JSON.
# """,
#     model=model,
#     handoffs=[education_summary_agent,job_summary_agent],
#     tools=[]
# )

@app.post("/triage")
async def handle_request(input_data: dict):
    try:
        user_input = "\n".join([f"{key.capitalize()}: {value}" for key, value in input_data.items()])
        
        education_result = await Runner.run(  
            education_summary_agent,
            user_input, 
             
        )
        job_result = await Runner.run(  
            job_summary_agent,
            user_input, 
              
        )
       
        print("this is education summary",education_result.final_output + "\n")
        print("this is job summary",    job_result.final_output + "\n")
        

        return {"education_summary": education_result.final_output,"job_summary": job_result.final_output}
    except Exception as e:
        return {"error": str(e)}
    

# Correct test for GET /
# if __name__ == "__main__":
#     client = TestClient(app)

#     test_data = {
#         "name": "John Doe",
#         "email": "john@example.com",
#         "number": "+1234567890",
#         "address": "123 Main St",
#         "degName": "BSc Computer Science",
#         "university": "Tech University",
#         "educationYear": "2023",
#          "position": "Software Engineer",
#         "company": "TechCorp",
#         "time": "2022 - Present",
#         "jobDescription": "Built APIs using FastAPI and integrated OpenAI SDK.",
#         "skills": ["Python", "FastAPI", "OpenAI", "Docker"],
#         "position": "Software Engineer",
#         "company": "TechCorp",
#         "time": "2022 - Present",
#         "jobDescription": "Built APIs using FastAPI and integrated OpenAI SDK.",
#         "skills": ["Python", "FastAPI", "OpenAI", "Docker"]
#     }

#     # Simulate POST request
# response = client.post("/triage", json=test_data)
# print(response.status_code)
# print(response.json())