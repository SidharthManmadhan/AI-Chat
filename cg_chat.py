#importing libraries
import streamlit as st
import requests
import json
import openai
from openai import OpenAI






# Set your OpenAI and MongoDB API keys




#user_input = st.text_input("Enter something:")
#st.write(f"You entered: {user_input}")

openai_api_key = st.secrets["openai_api_key"]
api_key_1 = st.secrets["api_key"]




client = OpenAI(api_key = openai_api_key)
# Function to send a chat completion request to the OpenAI API
def chat_completion_request(messages, tools=None, tool_choice=None, model="gpt-3.5-turbo"):
  response = client.chat.completions.create(
  model = "gpt-3.5-turbo",
  messages = messages,
  tools = tools,
  tool_choice = tool_choice)
  return response



def get_user_data(intents):
      url = "https://ap-south-1.aws.data.mongodb-api.com/app/data-kxpux/endpoint/data/v1/action/findOne"
      headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key': api_key_1,  # Replace 'your_api_key' with your actual API key
      }
    
    # Intent-to-collection mapping
      intent_to_collection = {
      'current_pathway_salary': "current_pathway",
      'switch_pathway': "other pathways",
      'career_progress': "user_journey",
      'recommended_skills': "user_journey",
      'recommended_employers': "top_employers",
      'job_details': "current_pathway",
      'learning': "courses",
      'resume_recommendation': "resume",
      'networking': 'user_profile',
      'interview_preparation': "interview preparation",
      'other': 'user_profile'
      }
    
    # Filter the collections based on the message intents
      intent_data = {}
      for intent in intents:
        collection = intent_to_collection.get(intent)
        if collection:
            payload = json.dumps({
                "collection": collection,
                "database": "cg_user",
                "dataSource": "Cluster0",
            })
            response = requests.post(url, headers=headers, data=payload)
            intent_data[intent] = response.json()  # Assume each response is JSON-decodable

      return intent_data




# Function to handle the continuous chat
def handle_chat():
  # a list to append user input and assistants response
  chat_history = []
  # list to hold intents of the user conversation
  intents = []
  #list to hold whole conversation including context,user input,prompt and assistants response
  messages = []
  
  if "streamlit_chat" not in st.session_state:
    st.session_state.streamlit_chat = []

  processed_intents = set()


 





  #URL to the mongodb database
  url = "https://ap-south-1.aws.data.mongodb-api.com/app/data-kxpux/endpoint/data/v1/action/findOne"

  # definining payload with headers to fetch current pathway data from MongoDB
  payload = json.dumps({
      "collection":"current_pathway",
      "database": "cg_user",
      "dataSource": "Cluster0",})

  headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key':api_key_1,}

  #post request to fetch required data
  response_1 = requests.request("POST", url, headers=headers, data=payload)
  # loading data to json
  response_1 = response_1.json()
  #current pathway name
  current_pathway = response_1["document"]["current_pathway"]["name"]
  # payload to fetch user profile data
  payload = json.dumps({
      "collection":"user_profile",
      "database": "cg_user",
      "dataSource": "Cluster0",})

  #post request to fetch required data
  response_2 = requests.request("POST", url, headers=headers, data=payload)
  #loading data to json
  response_2 = response_2.json()
  # name of the user
  name =   response_2["document"]["user_profile"]["name"]




  default_questions = [
      "Email Recruiter",
      "Interview Preparation",
      "Networking",
      "Upskilling",
      "Salary Negotiation",
      "Skills Demand"
  ]
  
  


 


  
  
  
  
  chat = st.chat_input()
  
  for question in default_questions:
    if st.button(question):
        chat = question  # Set 'chat' to the question from the button
        


  



  #user_input = st.text_input("You:", key="user_input")
  #submit = st.button('Send')

  #if submit:
        #if user_input.lower() == "exit":
            #st.stop()
        #else:
  if chat:
    user_input = chat
    context = f"""Your name is CareerGenie. You are a fun and engaging career advisor that answers in less than 100 words. If the conversation drifts into non-career topics, bring it back to career related topics. Name of the user is {name}. Current user pathway is {current_pathway}. """
    messages.append({"role": "system", "content": context})
    if len(messages) > 10:
      messages = messages[-10:]
      messages.insert(0, {"role": "system", "content": context})
    
    #User Input
    

# Processing user input when the button is pressed
        
    

    #appending user input to messages
    messages.append({"role": "user", "content": user_input})
# appending user input to the chat history
    chat_history.append({"role": "user", "content":user_input})

#Defining a tool to get the intent of user query

    tools_1 = [
                {
                "type": "function",
                "function":{
                    "name": "orchestrator",
                    "description": "Identify the intent of the user query.",
                    "parameters": {
                        "type": "object",
                            "properties": {
                                "intent_list": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["current_pathway_salary","switch_pathway","career_progress","recommended_skills","job_details","recommended_employers","learning","resume_recommendation","networking","interview_preparation","other",'greetings']
                                    },
                                    "description": "List of user intent",
                                }


                            },

                            "required": ["intent_list"],
                        },

                    },

                }

                ]


#Defining another tool to extract skills from course related queries.
    tools_2 = [
                {
                    "type": "function",
                    "function":{
                        "name": "learning_orchestrator",
                        "description": "Identify the skill that user want to learn.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "skills": {
                                    "type": "array",
                                        "items": {
                                            "type": "string",

                                        },
                                        "description": "Get the list of skills from the user query. If none are mentioned don't assume any skill.",
                                    }


                                },


                            },

                        },

                    }

                ]
#defining the tool choice
    tool_choice = {"type": "function", "function": {"name": "orchestrator"}}

#getting the response of user input using 'chat_completion_request' function
    chat_response = chat_completion_request(messages, tools=tools_1, tool_choice=tool_choice)  #getting the response of user input using 'chat_completion_request' function

#getting the intent of the user query from the response
    message = json.loads(chat_response.choices[0].message.tool_calls[0].function.arguments)["intent_list"]

    


    user_data = get_user_data(message)

    #Creating suitable prompts to handle the data based on different intents

    if message:
      prompt = "Understand the user query, and answer it strictly using the data provided. "
      for intent in message:
        if(intent == 'learning'):
            output = user_data.get(intent, {})
            tool_choice = {"type": "function", "function": {"name": "learning_orchestrator"}}
  #getting the response from chat_completion_request function
            chat_response_2 = chat_completion_request(messages, tools=tools_2, tool_choice=tool_choice)
                # getting argument value
            arguments = json.loads(chat_response_2.choices[0].message.tool_calls[0].function.arguments)
  # if skill is not present
            if not arguments :
                prompt = "Ask the user which particular skill or topic are they interested in learning about? Let us make sure we find the best resources for them! "
                Redirect_Message = " "
  #if skill is present                                                                                                                                         #What is it you want to learn?   In data we want one free course and 2 paid courses.
            else:
                skills = arguments['skills']
                skills = ', '.join(skills)
                skills = skills.lower()
                
                    #output = output[0]
                course_details = output["document"]["course_details"]
                #if skills from user query is present in the data, we fetch that particular course details from the data.
                courses_with_skills = [course for course in course_details if skills in course['skills']or skills in course['sub_skills']]
                prompt +=  f'For example, if user query is "how can I learn SQL?", answer with something like "Here are some courses that you should focus: " using the data provided.Make sure you have provided every course details associated with the user query. Data:{courses_with_skills}. "Tell the user that they can find courses related to your skills in the Role-Specific Skills section and the Cross-Functional Skills section in your {current_pathway} pathway.'
                Redirect_Message = " "

        if intent not in processed_intents:
          processed_intents.add(intent)

#prompt to answer salary related queries with salary data
        if (intent == 'current_pathway_salary'):
          output = user_data.get(intent, {})
          print(output)
          prompt +=  f'For example, if the user query is "What salary should I expect?", answer with something like "You can expect a salary range of around: " using the data provided. Data:{output}. '
          Redirect_Message = f"If you wish to check out salaries of other pathways tap the 'Switch' button on the top right of your {current_pathway} pathway section and select 'Add New Pathway' and feel free to explore other pathways and salaries."
  
  #prompt to answer queries related to other pathways with other pathways data
        if (intent == 'switch_pathway'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'For example, if the user query is ""What career pathways do you recommend for someone with my skill set?", answer with something like "Based on your skill set, I would recommend exploring pathways in: " using the data provided. Data:{output}. '
            Redirect_Message = f"Check out more pathways by tapping the 'Switch' button on the top right of your {current_pathway} pathway and select 'Add New Pathway' and explore other pathways."
    
        #prompt to answer queries related to career progression with user journey data
        if(intent == 'career_progress'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'For example, if the user query is "What are the next steps I should take in my career path?", answer with something like "As a next step you should focuss on these skills and these pathways: " using the data provided. Data:{output}. '
            Redirect_Message = "Look into Connecting with experts in the job application section of the app. And take a look into our courses to master these skills."
    
        #propmt to answer queries related to skills recommendation with user journey data
        if(intent == 'recommended_skills'):
            output = user_data.get(intent, {})
            print(output)
            prompt +=  f'For example, if the user query is "What skills am I lacking for my desired job role?", answer with something like "Based on your desired job role you should focuss on these skills: " using the data provided. Data:{output}. '
            Redirect_Message = "Take a look into our courses in the Role specific skills section to master these skills."
    
        #prompt to answer quries related to employer recommendation with top employers data
        if(intent == 'recommended_employers'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'For example, if the user query is "Which companies should I apply to?", answer with something like "Here are few employers that are looking for talented people like you: " using the data provided. Data:{output}. '
            Redirect_Message = " "
    
        #propmt to answer queries related to job details with job data
        if(intent == 'job_details'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'For example, if user query is "What jobs should I apply to?", answer with something like "Here are some job titles that you should focus on given your skills and interests: " using the data provided. Data:{output}. '
            Redirect_Message = "Check out open jobs that match your career pathway in the job application section of the app."
    
    #prompt to answer resume related queries
        if (intent == 'resume_recommendation'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'For example, if the user query is "how to make my resume better", provide usefull 4-5 tips to improve the resume. Resume Text:{output}. '
            Redirect_Message = f"For a more thorough review, you can also use the Resume Checker feature in the Job Application section in your {current_pathway} pathway, which would provide detailed feedback on your resume"
    
        #prompt to answer queries related to networking
        if (intent == 'networking'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'For example, if the user query is "how to improve my network based on my pathway?", provide useful tips for connecting with professionals on linkedin based on user profile. User Profile:{output}. '
            Redirect_Message = 'You can automatically filter relevant professionals on linkedin by using the Connect with Experts section in your Job Application phase.'
    
        #prompt to answer queries related to interviews
        if (intent == 'interview_preparation'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'For example, if user query is "How do I prepare for interviews?", provide useful tips for interviews and suggest practicing questions like answer with something like "Here are some questions that will help you in technical interviews: " using the data provided. Data:{output}. '   #prompt to answer queries related to interviews
            Redirect_Message  = "If you want to conduct a mock interview check out the Interview Preparation section in your app."
    
        #prompt to answer other queries which is not related to any of the intent
        if (intent == 'other'):
            output = user_data.get(intent, {})
            print(output)
            prompt += f'User Profile: {output}'
            Redirect_Message = ''

        if(intent == "greetings"):
           prompt += "Greet back the user."
           Redirect_Message = ''
           
           
           

      #appending prompt to messages
    messages.append({"role": "system", "content": prompt})
    #passing the messages to the next 'chat_completion_request' function to get the last response
    assistants_response = chat_completion_request(messages)
    assistants_response = assistants_response.choices[0].message.content
    #appending the assistants response to messages to hold full conversation
    messages.append({"role": "assistant", "content": assistants_response})
  
    
  
   
  
    #appending the intent to intents list
    intents.append(message)
    #checking intents are repeating, if repeating we will pass the 'Redirect_Message' only once
    flat_list = [item for sublist in intents for item in sublist]
  
    if len(set(flat_list)) < len(flat_list):
        assistants_response = assistants_response
  
    else:
      assistants_response = assistants_response + ' ' + Redirect_Message
    
  
    st.session_state.streamlit_chat.append({"user": user_input, "assistant": assistants_response})
  
    for index, chat in  enumerate(st.session_state.streamlit_chat):
        st.text_area("User", value=chat["user"], height=100, disabled= False, key=f"user_{index}")
        st.text_area("Assistant", value=chat["assistant"], height=300, disabled=False, key=f"assistant_{index}")

        
        
      
  

    
    

# Main function to start the chat
if __name__ == "__main__":
  handle_chat()

