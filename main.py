from fastapi import FastAPI
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel 
from agents.run import RunConfig
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware



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


triage_agent = Agent(
    name="Triage Agent",
    instructions="You are an expert project or working manager, defining and giving task to your employee, give the education details to the education summary agent, and then return the summary which the agent provides",
    model=model,
    handoffs=[education_summary_agent],
    tools=[]
)

@app.post("/triage")
async def handle_request(input_data: dict):
    try:
        user_input = "\n".join([f"{key.capitalize()}: {value}" for key, value in input_data.items()])
        # print(user_input)
        result = await Runner.run(  
            triage_agent,
            user_input, 
              # or just input_data if it's a string
        )
        print(result.final_output)

        return {"summary": result.final_output}
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